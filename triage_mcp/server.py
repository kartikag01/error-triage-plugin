"""MCP server `error-triage` (stdio). Three tools, read + resolve only (no ingestion).

Env:
  TRIAGE_API_URL    base URL of the triage service (default http://127.0.0.1:8000)
  TRIAGE_AUTOSTART  "1" = start the service + seed demo data if it is not running
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import httpx  # noqa: E402
from mcp.server.fastmcp import FastMCP  # noqa: E402

API = os.getenv("TRIAGE_API_URL", "http://127.0.0.1:8000").rstrip("/")
mcp = FastMCP("error-triage")


def _healthy() -> bool:
    try:
        return httpx.get(f"{API}/health", timeout=1.5).status_code == 200
    except httpx.HTTPError:
        return False


def _ensure_api() -> None:
    if _healthy():
        return
    if os.getenv("TRIAGE_AUTOSTART") != "1":
        raise RuntimeError(
            f"Triage service is not reachable at {API}. Start it with "
            "`python -m uvicorn triage_service.main:app --port 8000` and run `python scripts/seed.py`, "
            "or set TRIAGE_AUTOSTART=1 for the MCP server."
        )
    port = API.rsplit(":", 1)[-1].split("/")[0]
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "triage_service.main:app", "--port", port, "--log-level", "warning"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(40):
        if _healthy():
            break
        time.sleep(0.25)
    else:
        raise RuntimeError("Triage service failed to start")
    from scripts.seed import seed  # imported lazily

    seed(API, ROOT / "data" / "errors.jsonl", reset=True)


def _call(method: str, path: str, **kwargs):
    _ensure_api()
    resp = httpx.request(method, f"{API}{path}", timeout=10, **kwargs)
    if resp.status_code == 404:
        raise ValueError(resp.json().get("detail", "not found"))
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def list_error_groups(window_minutes: int = 120, min_count: int = 1, include_resolved: bool = False) -> list[dict]:
    """List grouped production errors ranked by urgency (highest first).

    Use this first when asked to triage, investigate or review recent errors.
    Each group has: id, title, exception, top_frame (file + function of the failing app code),
    count within the window, first/last seen, services, urgency score, and
    started_after_deploy (true if the group first appeared after the latest deploy).

    Args:
        window_minutes: look-back window in minutes (default 120).
        min_count: hide groups with fewer occurrences than this (default 1).
        include_resolved: also return groups already marked resolved (default false).
    """
    return _call("GET", "/groups", params={
        "window_minutes": window_minutes, "min_count": min_count, "include_resolved": include_resolved})


@mcp.tool()
def get_group_details(group_id: str) -> dict:
    """Get full details for one error group: sample messages, the stack trace (app frames first),
    the latest deploy version and time. Use after list_error_groups, on the group you plan to fix.

    Args:
        group_id: the `id` field from list_error_groups.
    """
    return _call("GET", f"/groups/{group_id}")


@mcp.tool()
def mark_group_resolved(group_id: str, note: str = "") -> dict:
    """Mark an error group as resolved once a fix and regression test exist.
    Only call this after the fix is applied and tests pass.

    Args:
        group_id: the `id` field from list_error_groups.
        note: short description of the fix (shown to the team).
    """
    return _call("POST", f"/groups/{group_id}/resolve", json={"note": note})


if __name__ == "__main__":
    mcp.run()
