# Live demo (about 8 minutes)

## Setup (before going on stage)
```bash
python -m uvicorn triage_service.main:app --port 8000     # terminal 1
python scripts/seed.py --reset                            # terminal 2 (re-run right before the demo)
git checkout -- sample_app/                               # restore the buggy code
```
Open the repo in VS Code. Close all editor tabs except this script.

## Flow
| Time | Say | Show |
|---|---|---|
| 0:00 | "260 raw errors. Nobody reads 260 errors." | `head -3 data/errors.jsonl` |
| 0:45 | "Here is the microservice. Ingest, group, score." | `http://127.0.0.1:8000/docs`, then `GET /groups` |
| 1:45 | "An MCP server turns three endpoints into three tools. The docstring is the API for the model." | `triage_mcp/server.py` (tool docstrings only) |
| 2:45 | "Plugin = command + agent + skills + hooks + MCP in one folder." | `plugin.json`, folder tree |
| 3:30 | **Type `/triage`** | Chat output: top group is `KeyError 'customer'`, started after v2.4.1; timeouts skipped as upstream noise |
| 5:00 | "It asks before touching code." | Diff for `orders/service.py`; approve |
| 5:45 | "Then a regression test, then it runs it." | New test, green run |
| 6:30 | "Resolved only because tests passed." | `mark_group_resolved` call |
| 7:00 | "A hook, not a prompt, guarantees this." | Ask the agent to `rm -rf` something: guard hook blocks it; show `.triage/audit.log` |
| 7:45 | "Push to Git, teammates install it." | `@agentPlugins` view |

## Expected agent behaviour
- Top group: `KeyError: 'customer'` in `sample_app/orders/service.py` (about 214 events, started after v2.4.1).
- Skipped: `TimeoutError` payment gateway (pre-dates the deploy), invalid-quantity `ValueError`, one cache blip.
- Likely fix: read `order.get("customer")` and handle guest checkout (no customer id). Any equivalent minimal fix is fine.

## If something goes wrong
- **Model takes a different path:** keep going, narrate it. Tools and approvals are the point.
- **Service not reachable:** `TRIAGE_AUTOSTART=1` in the MCP env starts it for you.
- **Wi-Fi or model slow:** play the backup recording.
- **Reset between rehearsals:** `python scripts/seed.py --reset` and `git checkout -- sample_app/`.

## Optional: ship as a `.vsix`
Wrap the same MCP server in a VS Code extension (`mcpServerDefinitionProviders` contribution) and package with `vsce package`. Check the current extension API for MCP registration against your VS Code version before the talk.
