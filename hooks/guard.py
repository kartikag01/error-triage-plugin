"""PreToolUse hook: deterministically block destructive commands (a prompt can't guarantee this).

Reads the hook payload (JSON) on stdin. Exit code 2 = block, and stderr is shown to the agent.
"""
import json
import re
import sys

DANGEROUS = [
    r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\b", r"\bdrop\s+(table|database)\b", r"\bgit\s+push\s+.*--force\b",
    r"\bgit\s+reset\s+--hard\b", r"\bformat\s+[a-z]:", r"\bdel\s+/[sqf]\b", r"\bcurl\b.*\|\s*(sh|bash)\b",
]

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # never break the agent because of a malformed payload

text = json.dumps(payload.get("tool_input", payload))
for pattern in DANGEROUS:
    if re.search(pattern, text, re.IGNORECASE):
        sys.stderr.write(f"Blocked by error-triage guard hook: matched /{pattern}/. Ask the user first.\n")
        sys.exit(2)
sys.exit(0)
