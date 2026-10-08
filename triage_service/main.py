"""FastAPI microservice. Run: python -m uvicorn triage_service.main:app --port 8000"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from .models import ErrorEvent, GroupDetail, GroupSummary, ResolveRequest
from .store import store

app = FastAPI(title="Error Triage Service", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest")
def ingest(events: list[ErrorEvent]) -> dict:
    """Accept a batch of log events (what a log shipper or app handler would POST)."""
    for event in events:
        store.add(event)
    return {"accepted": len(events)}


@app.get("/groups", response_model=list[GroupSummary])
def list_groups(
    window_minutes: int = Query(120, ge=1, le=10080),
    min_count: int = Query(1, ge=1),
    include_resolved: bool = False,
) -> list[GroupSummary]:
    return store.list_groups(window_minutes, min_count, include_resolved)


@app.get("/groups/{group_id}", response_model=GroupDetail)
def get_group(group_id: str) -> GroupDetail:
    group = store.get_group(group_id)
    if group is None:
        raise HTTPException(404, f"No such group: {group_id}")
    return group


@app.post("/groups/{group_id}/resolve")
def resolve_group(group_id: str, body: ResolveRequest) -> dict:
    if not store.resolve(group_id, body.note):
        raise HTTPException(404, f"No such group: {group_id}")
    return {"id": group_id, "resolved": True, "note": body.note}


@app.get("/deploys")
def deploys() -> list[dict]:
    return store.deploys()


@app.post("/reset")
def reset() -> dict:
    """Demo helper: wipe all data so you can re-seed between rehearsals."""
    store.reset()
    return {"reset": True}
