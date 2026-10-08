"""End-to-end: launch the MCP server over stdio with TRIAGE_AUTOSTART and call the tools."""
import json
import socket
import sys
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_mcp_tools_end_to_end():
    port = free_port()

    async def run():
        params = StdioServerParameters(
            command=sys.executable, args=[str(ROOT / "triage_mcp" / "server.py")],
            env={"TRIAGE_AUTOSTART": "1", "TRIAGE_API_URL": f"http://127.0.0.1:{port}"},
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = {t.name for t in (await session.list_tools()).tools}
                assert tools == {"list_error_groups", "get_group_details", "mark_group_resolved"}
                res = await session.call_tool("list_error_groups", {"window_minutes": 120})
                groups = json.loads(res.content[0].text) if len(res.content) == 1 else [json.loads(c.text) for c in res.content]
                top = groups[0]
                assert top["exception"] == "KeyError" and top["started_after_deploy"]
                detail = json.loads((await session.call_tool("get_group_details", {"group_id": top["id"]})).content[0].text)
                assert detail["sample_stack"][0].startswith("sample_app/orders/service.py")

    anyio.run(run)
