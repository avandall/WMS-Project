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

## 🌍 Cloudflare Tunnel (Optional)

This repo includes a `cloudflared` service in `docker-compose.yml` under the `tunnel` profile.

```bash
docker compose --profile tunnel up -d --build
docker compose logs -f tunnel
```

See `cloudflare/README.md` for named-tunnel (custom domain) setup.

## 🤖 AI (LangChain) – Chat DB

This project exposes a read-only DB chat endpoint backed by LangChain.

1) Configure `.env` (see `.env.example`) with `DATABASE_URL`, `AI_PROVIDER`, `AI_MODEL`, and your provider API key.

2) Run the server (see Quick Start).

3) Call the endpoint:

```bash
curl -X POST http://127.0.0.1:8080/api/ai/chat-db \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <YOUR_JWT>' \
  -d '{"message": "How many products do we have?"}'
```

Direct python usage (no HTTP):

```python
from app.ai_engine import handle_customer_chat_with_db

result = handle_customer_chat_with_db("List 10 newest documents")
print(result["answer"])
print(result["sql"])
```

## Tests

From `WMS/`:

```powershell
pytest
```
