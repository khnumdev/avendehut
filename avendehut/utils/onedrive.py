from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from msgraph import GraphServiceClient  # type: ignore
from azure.identity import ClientSecretCredential  # type: ignore


def is_onedrive_path(path: str) -> bool:
  return path.startswith("onedrive:/")


def ensure_onedrive_env() -> None:
  required = ["ONEDRIVE_CLIENT_ID", "ONEDRIVE_CLIENT_SECRET", "ONEDRIVE_TENANT_ID"]
  missing = [k for k in required if not os.getenv(k)]
  if missing:
    raise RuntimeError(f"Missing OneDrive environment variables: {', '.join(missing)}")


def _get_graph_client() -> GraphServiceClient:
  tenant_id = os.environ["ONEDRIVE_TENANT_ID"]
  client_id = os.environ["ONEDRIVE_CLIENT_ID"]
  client_secret = os.environ["ONEDRIVE_CLIENT_SECRET"]
  credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
  # Use app-only default scope for Microsoft Graph
  scopes = ["https://graph.microsoft.com/.default"]
  return GraphServiceClient(credential=credential, scopes=scopes)


def _list_children_once(client: GraphServiceClient, rel_path: str):
  if rel_path.strip("/"):
    return client.me.drive.root.item_with_path(rel_path).children.get()
  return client.me.drive.root.children.get()


def _iterate_children(client: GraphServiceClient, rel_path: str):
  collection = _list_children_once(client, rel_path)
  while True:
    if collection and getattr(collection, "value", None):
      for it in collection.value:
        yield it
    next_link = getattr(collection, "odata_next_link", None)
    if not next_link:
      break
    # Follow next link via SDK request adapter
    collection = client._client._request_adapter.send_async(  # type: ignore[attr-defined]
      request_info=client._client._request_adapter.base_url_provider.clone_request_information(next_link),  # type: ignore[attr-defined]
      response_type=type(collection),
    ).result()


def list_onedrive_files(prefix_path: str) -> Iterable[Path]:  # pragma: no cover - network
  """List files under the given OneDrive path using Microsoft Graph (app-only).

  Returns Path objects with the pseudo scheme 'onedrive:/...'. Only files are returned; folders
  are traversed recursively.
  """
  if not is_onedrive_path(prefix_path):
    raise ValueError("prefix_path must start with 'onedrive:/'")

  ensure_onedrive_env()
  client = _get_graph_client()

  rel = prefix_path[len("onedrive:/"):].lstrip("/")
  stack = [rel]
  while stack:
    current_rel = stack.pop()
    for it in _iterate_children(client, current_rel):
      if getattr(it, "folder", None) is not None:
        child_rel = f"{current_rel}/{it.name}" if current_rel else it.name
        stack.append(child_rel)
      else:
        path_str = f"onedrive:/{current_rel}/{it.name}" if current_rel else f"onedrive:/{it.name}"
        yield Path(path_str.replace("//", "/"))

