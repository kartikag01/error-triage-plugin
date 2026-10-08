# error-triage: an agent plugin for VS Code

A reusable plugin that lets an AI agent **triage production errors**: it groups raw errors, ranks them by urgency, finds the failing code in your workspace, proposes a fix, adds a regression test, and marks the group resolved.

It bundles every part of the agent-customization stack in one installable unit:

| Piece | Where | What it does |
|---|---|---|
| Microservice | `triage_service/` | FastAPI: `POST /ingest`, `GET /groups`, `GET /groups/{id}`, `POST /groups/{id}/resolve` |
| MCP server | `triage_mcp/server.py` | Tools: `list_error_groups`, `get_group_details`, `mark_group_resolved` |
| Slash command | `commands/triage.md` | `/triage` entry point |
| Custom agent | `agents/triage-oncall.agent.md` | Scoped tools, approval-before-edit workflow |
| Agent Skills | `skills/error-triage`, `skills/regression-test` | Prioritisation rules, stack-trace guide, test conventions |
| Hooks | `hooks.json`, `hooks/` | `guard.py` blocks destructive commands, `audit_log.py` logs actions |
| Instructions | `.github/copilot-instructions.md`, `.github/instructions/` | Conventions for contributors to this repo |
| Seed data | `data/errors.jsonl` | 260 synthetic events with a built-in story |
| Sample app | `sample_app/` | A deliberately buggy order service for the agent to fix |

## Quick start (local demo)

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q                                      # 10 tests should pass

# terminal 1: the microservice
python -m uvicorn triage_service.main:app --port 8000
# terminal 2: load demo data (re-run anytime)
python scripts/seed.py --reset
```

Open this folder in VS Code. `.vscode/mcp.json` registers the MCP server for the workspace. In Copilot Chat (agent mode) run:

```
/triage
```

## Install as a plugin (for your team)

1. Push this repo to GitHub.
2. Teammates: Extensions view → search `@agentPlugins`, or Command Palette → `Chat: Plugins`, and install from the repo. With Copilot CLI: `copilot plugin install <owner>/<repo>`.
3. Teammates need Python 3.11+ and `pip install -r requirements.txt` in the plugin folder once.
4. The plugin's `.mcp.json` sets `TRIAGE_AUTOSTART=1`, so the MCP server starts the service and loads the demo data itself if nothing is running.

> **Verify before sharing (agent plugins are in preview):** the exact plugin-root token in `.mcp.json` / `hooks.json` (`${CLAUDE_PLUGIN_ROOT}`), the tool-name syntax in `agents/triage-oncall.agent.md` (`error-triage/*`) and the hook event names can differ by VS Code version. Check them against https://code.visualstudio.com/docs/agent-customization/agent-plugins and fix if needed.

## Point it at real errors

Replace the seed step: have your app or log shipper `POST` batches of events to `/ingest` (see `triage_service/models.py` for the `ErrorEvent` schema). Swap the in-memory store in `store.py` for a database before using it for anything real.

## Develop

```bash
make test      # or: python -m pytest -q
make data      # regenerate data/errors.jsonl
```

Docs: [`docs/PLAN.md`](docs/PLAN.md) (build plan), [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) (8-minute live demo).

## Safety notes
- All data is synthetic. Do not commit real logs.
- Plugins can run hooks and MCP servers on your machine: review `hooks/` and `triage_mcp/` before installing anything from a repo, including this one.
