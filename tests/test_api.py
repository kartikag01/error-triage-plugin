from pathlib import Path

from fastapi.testclient import TestClient

from scripts.seed import load_events
from triage_service.main import app

client = TestClient(app)
DATA = Path(__file__).resolve().parent.parent / "data" / "errors.jsonl"


def seeded():
    client.post("/reset")
    assert client.post("/ingest", json=load_events(DATA)).json()["accepted"] == 260


def test_seed_collapses_into_few_groups_and_top_is_the_deploy_bug():
    seeded()
    groups = client.get("/groups").json()
    assert 3 <= len(groups) <= 6
    top = groups[0]
    assert top["exception"] == "KeyError"
    assert top["started_after_deploy"] is True
    assert top["count"] > 100
    assert "orders/service.py" in top["top_frame"]


def test_timeouts_are_noise_not_after_deploy():
    seeded()
    timeout = next(g for g in client.get("/groups").json() if g["exception"] == "TimeoutError")
    assert timeout["started_after_deploy"] is False


def test_details_and_resolve():
    seeded()
    gid = client.get("/groups").json()[0]["id"]
    detail = client.get(f"/groups/{gid}").json()
    assert detail["sample_stack"][0].startswith("sample_app/orders/service.py:9")
    assert detail["last_deploy_version"] == "v2.4.1"
    assert client.post(f"/groups/{gid}/resolve", json={"note": "fixed"}).json()["resolved"] is True
    assert all(g["id"] != gid for g in client.get("/groups").json())
    assert any(g["id"] == gid for g in client.get("/groups?include_resolved=true").json())


def test_unknown_group_404():
    assert client.get("/groups/nope").status_code == 404
