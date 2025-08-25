## avendehut

A CLI tool to scan a folder of books (local or OneDrive), extract metadata, generate tags, and produce a searchable HTML catalog.

Inspired by the historical figure [Juan Hispalense (siglo XII)](https://es.wikipedia.org/wiki/Juan_Hispalense_%28siglo_XII%29), also known as Avendehut Hispanus.

### Features

- **📚 Metadata extraction**: EPUB, PDF, MOBI (extensible to other formats).
- **🏷 Automatic tag generation**: From metadata and file content.
- **🌐 HTML catalog generation**:
  - Generates `index.html`, `data.json`, and static assets.
  - Searchable, filterable, and responsive UI.
  - Supports tag filtering, instant search, and lazy loading for large datasets.
- **⚡ Incremental builds**: Uses a `.manifest.json` to skip unchanged files.
- **☁ OneDrive integration**: Via Microsoft Graph API.
- **🔍 CLI search**: Search without opening the HTML site.
- **📤 Export catalog**: To CSV or JSON.
- **🖥 Cross‑platform**: macOS and Linux.

### Requirements

- **OS**: macOS or Linux
- **Python**: 3.10+
- **Dependency management**: Poetry
- **For OneDrive integration**:
  - Microsoft account
  - Microsoft Graph API app registration

### Installation

1. Clone the repository.
   ```bash
   git clone https://github.com/khnumdev/avendehut.git
   cd avendehut
   ```
2. Install dependencies with Poetry.
   ```bash
   poetry install
   ```
3. Set environment variables for OneDrive (if needed).
   - `ONEDRIVE_CLIENT_ID`
   - `ONEDRIVE_CLIENT_SECRET`
   - `SRC_FOLDER` (OneDrive folder path)
   - `OUT_FOLDER` (local output path)

### OneDrive Setup

- If `--src` points to a OneDrive path, the tool uses Microsoft Graph API.
- Required environment variables:
  - `ONEDRIVE_CLIENT_ID`
  - `ONEDRIVE_CLIENT_SECRET`
  - `ONEDRIVE_TENANT_ID`
  - `SRC_FOLDER` (OneDrive folder path)
  - `OUT_FOLDER` (local output path)
- Register an app and configure permissions by following Microsoft's official docs: [Register an application](https://learn.microsoft.com/en-us/graph/auth-register-app-v2).

### CLI Commands

| Command | Description | Options |
| --- | --- | --- |
| `avendehut build` | Scans source folder, processes new/updated books, generates HTML site. | `--src <path>` (source folder), `--out <path>` (output folder), `--format html` (default), `--force` (reprocess all) |
| `avendehut watch` | Watches source folder for changes, auto‑rebuilds HTML. | Same as build plus `--interval <seconds>` |
| `avendehut clean` | Deletes generated output and manifest. | `--out <path>` |
| `avendehut open` | Opens generated HTML in default browser. | `--out <path>` |
| `avendehut search` | CLI search in local index. | `--query "<text>"`, `--tags "<tag1,tag2>"` |
| `avendehut export` | Exports catalog to CSV or JSON. | `--out <file>`, `--format csv|json` |

### Usage

```bash
# Build a catalog from a local folder
poetry run avendehut build --src ./books --out ./dist

# Open the generated HTML
poetry run avendehut open --out ./dist

# Search from the CLI
poetry run avendehut search --out ./dist --query "Dune" --tags "sci-fi,epub"

# Export catalog
poetry run avendehut export --src-out ./dist --format csv --out ./dist/catalog.csv
```

### HTML Catalog Features

- Responsive design (mobile, tablet, desktop).
- Instant search with highlighting.
- Tag filtering (multi‑select).
- Lazy loading for large datasets.
- Split `data.json` into chunks if > 5 MB.
- Keyboard shortcuts for navigation.
- Dark mode toggle.

### CI/CD Integration

- Use GitHub Actions for:
  - Linting (`flake8`, `black`).
  - Running tests (`pytest`).
  - Building HTML output.
  - Deploying to GitHub Pages (optional).

- Example workflow:
  - Trigger on push to `main`.
  - Install Python & Poetry.
  - Run `poetry install`, `poetry run pytest`.
  - If tests pass, run `avendehut build` and deploy.

### Development Guide

- Run in development mode: `poetry run avendehut --help`.
- Add new commands: extend the CLI module and register the command.
- Extend metadata extraction: add new extractor classes/modules.
- Contribute: see [`CONTRIBUTORS.md`](CONTRIBUTORS.md).

### License

Apache 2.0 License.

# avendehut