"""Load data/errors.jsonl into the running service via POST /ingest.

Usage: python scripts/seed.py [--api URL] [--file PATH] [--reset]
Timestamps are rebased so `minutes_ago` is relative to *now*.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent


def load_events(path: Path) -> list[dict]:
    now = datetime.now(timezone.utc)
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        minutes = raw.pop("minutes_ago", 0)
        raw["ts"] = (now - timedelta(minutes=minutes)).isoformat()
        events.append(raw)
    return events


def seed(api: str, path: Path, reset: bool) -> int:
    events = load_events(path)
    with httpx.Client(base_url=api, timeout=10) as client:
        if reset:
            client.post("/reset").raise_for_status()
        resp = client.post("/ingest", json=events)
        resp.raise_for_status()
        return resp.json()["accepted"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default=os.getenv("TRIAGE_API_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--file", default=str(ROOT / "data" / "errors.jsonl"))
    parser.add_argument("--reset", action="store_true", help="wipe the service before seeding")
    args = parser.parse_args()
    print(f"seeded {seed(args.api, Path(args.file), args.reset)} events into {args.api}")
