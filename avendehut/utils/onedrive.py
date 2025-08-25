from __future__ import annotations

import os
from pathlib import Path
from typing import Generator, Iterable, List

from msgraph import GraphServiceClient  # type: ignore
from azure.identity import DeviceCodeCredential  # type: ignore
import requests


def is_onedrive_path(path: str) -> bool:
  return path.startswith("onedrive:/")


def ensure_onedrive_env() -> None:
  required = ["ONEDRIVE_CLIENT_ID"]
  missing = [k for k in required if not os.getenv(k)]
  if missing:
    raise RuntimeError(f"Missing OneDrive environment variables: {', '.join(missing)}")


def _get_graph_client() -> GraphServiceClient:
  client_id = os.environ["ONEDRIVE_CLIENT_ID"]
  tenant_id = os.environ.get("ONEDRIVE_TENANT_ID", "consumers")
  # Device code credential prompts user in terminal to authenticate once and caches token
  credential = DeviceCodeCredential(client_id=client_id, tenant_id=tenant_id)
  scopes = ["Files.Read.All"]
  client = GraphServiceClient(credential=credential, scopes=scopes)
  return client


def _enumerate_children_with_paging(client: GraphServiceClient, rel_path: str) -> List[dict]:
  # First page via SDK
  if rel_path.strip("/"):
    collection = client.me.drive.root.item_with_path(rel_path).children.get()
  else:
    collection = client.me.drive.root.children.get()

  items: List[dict] = []
  if collection and getattr(collection, "value", None):
    for it in collection.value:
      items.append(it.__dict__)

  # Follow @odata.nextLink using raw requests with the same credential
  next_link = getattr(collection, "odata_next_link", None)
  if next_link:
    # Acquire bearer token for request
    credential = client._client._config.authentication_provider._scopes_credential  # type: ignore[attr-defined]
    # Fallback: create our own credential if not accessible
    token = None
    try:
      token = credential.get_token("Files.Read.All")
    except Exception:
      cred = DeviceCodeCredential(client_id=os.environ["ONEDRIVE_CLIENT_ID"], tenant_id=os.environ.get("ONEDRIVE_TENANT_ID", "consumers"))
      token = cred.get_token("Files.Read.All")
    headers = {"Authorization": f"Bearer {token.token}", "Accept": "application/json"}
    url = next_link
    while url:
      resp = requests.get(url, headers=headers, timeout=30)
      resp.raise_for_status()
      data = resp.json()
      for it in data.get("value", []):
        items.append(it)
      url = data.get("@odata.nextLink")

  return items


def list_onedrive_files(prefix_path: str) -> Iterable[Path]:  # pragma: no cover - network
  """List files under the given OneDrive path using Microsoft Graph SDK with pagination.

  Returns Path objects with the pseudo scheme 'onedrive:/...'. Only files are returned; folders
  are traversed recursively.
  """
  if not is_onedrive_path(prefix_path):
    raise ValueError("prefix_path must start with 'onedrive:/'")

  ensure_onedrive_env()
  client = _get_graph_client()

  # Normalize to relative path within drive root
  rel = prefix_path[len("onedrive:/"):].lstrip("/")

  stack = [rel]
  while stack:
    current_rel = stack.pop()
    for it in _enumerate_children_with_paging(client, current_rel):
      # If it is a folder, descend
      if it.get("folder") is not None:
        child_rel = f"{current_rel}/{it.get('name')}" if current_rel else it.get("name")
        stack.append(child_rel)
      else:
        # File item
        path_str = f"onedrive:/{current_rel}/{it.get('name')}" if current_rel else f"onedrive:/{it.get('name')}"
        # Clean double slashes
        path_str = path_str.replace("//", "/")
        yield Path(path_str)

