"""PostToolUse hook: append triage-relevant tool calls to .triage/audit.log (deterministic audit trail)."""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool = str(payload.get("tool_name") or payload.get("toolName") or "")
if not re.search(r"triage|edit|write|replace|test", tool, re.IGNORECASE):
    sys.exit(0)

summary = json.dumps(payload.get("tool_input", {}))[:200]
log = Path(".triage") / "audit.log"
log.parent.mkdir(exist_ok=True)
with log.open("a", encoding="utf-8") as fh:
    fh.write(f"{datetime.now(timezone.utc).isoformat()}\t{tool}\t{summary}\n")
sys.exit(0)
