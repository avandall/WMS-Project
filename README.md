# Warehouse Management System (WMS)

A comprehensive Warehouse Management System built with Python, FastAPI, and Clean Architecture.

## Repository Structure

- `WMS/` — the main FastAPI WMS application (this is the project you run)
- `dashboard/` — static dashboard assets (demo)
- `check_db.py`, `test_api.py` — small utilities / integration checks

## 🚀 Quick Start (API)

From the repo root:

```bash
cd WMS
```

Install dependencies:

```bash
uv sync
# or, without uv:
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run the server:

```bash
uv run python src/main.py
# or:
python src/main.py
```

## 🌐 Dashboard (Demo)

```bash
cd dashboard
python -m http.server 8080
```

Open http://127.0.0.1:8080 in your browser.

## Tests

From `WMS/`:

```powershell
pytest
```
