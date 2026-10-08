# Repository instructions

This repo contains an **error-triage** agent plugin: a FastAPI service (`triage_service/`), an MCP server (`triage_mcp/`), seed data (`data/`), a deliberately buggy sample app (`sample_app/`) and the plugin assets (`agents/`, `commands/`, `skills/`, `hooks/`, `plugin.json`).

- Python 3.11+, type hints on public functions, `pytest` for tests (`python -m pytest -q`).
- `sample_app/` is **intentionally buggy**. Do not "clean it up" outside the triage demo flow.
- Data is synthetic. Never add real logs, customer data or secrets.
- MCP tool docstrings are the model-facing API: keep them accurate and specific.
- Keep ingestion out of the MCP server: agents read and resolve, they never write raw data.
