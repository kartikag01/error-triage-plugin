# Build plan

| # | Phase | Output | Done when |
|---|---|---|---|
| 1 | Microservice | `triage_service/` | `/ingest`, `/groups`, `/groups/{id}`, `/resolve` work; fingerprint tests pass |
| 2 | Data + sample app | `data/errors.jsonl`, `sample_app/` | 260 events collapse into 4 groups; top group is the post-deploy `KeyError` |
| 3 | MCP server | `triage_mcp/server.py` | 3 tools listed over stdio; end-to-end test passes |
| 4 | Agent assets | agent, command, 2 skills | `/triage` runs the 9-step workflow in VS Code |
| 5 | Hooks | `guard.py`, `audit_log.py` | Destructive command is blocked; audit log written |
| 6 | Packaging | `plugin.json`, `.mcp.json`, `hooks.json` | Installs via `@agentPlugins` on a clean machine |
| 7 | Share | GitHub repo + CI | Teammate installs and runs `/triage` in under 5 minutes |

## Design decisions
- **Ingestion lives in the service, not in MCP.** Agents read and resolve; they never write raw data.
- **Fingerprint = exception type + first app frame (no line number) + normalised message.** Stable across edits.
- **Urgency = count x (0.5 + recency) x 1.5 if after deploy.** Simple enough to explain on a slide.
- **In-memory store.** Re-seed on start. Swap for SQLite/Postgres for real use.
- **Approval before edit** is encoded in the agent and command, so the audience sees a human-in-the-loop pattern.

## Before the talk
- [ ] Rehearse `/triage` 3 times on the seeded data
- [ ] Record a backup screen capture of the full run
- [ ] Confirm plugin format details against your VS Code version (see README)
- [ ] Pre-install dependencies and pre-warm the service
- [ ] Decide marketplace vs plugin story (a `.vsix` wrapper is a separate step, see DEMO_SCRIPT)
