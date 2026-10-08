"""In-memory store. Re-seed on startup; swap for SQLite/Postgres when you productionise."""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from .fingerprint import exception_type, fingerprint, top_app_frame
from .models import ErrorEvent, GroupDetail, GroupSummary
from .scoring import urgency


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


@dataclass
class _Group:
    id: str
    exception: str
    top_frame: str
    title: str
    timestamps: list[datetime] = field(default_factory=list)
    services: set[str] = field(default_factory=set)
    sample_messages: list[str] = field(default_factory=list)
    sample_stack: list[str] = field(default_factory=list)
    resolved: bool = False
    resolved_note: str = ""


class Store:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._groups: dict[str, _Group] = {}
        self._deploys: list[tuple[datetime, str]] = []

    def reset(self) -> None:
        with self._lock:
            self._groups.clear()
            self._deploys.clear()

    def add(self, event: ErrorEvent) -> None:
        ts = _aware(event.ts)
        with self._lock:
            if event.type == "deploy":
                self._deploys.append((ts, event.version or "unknown"))
                self._deploys.sort()
                return
            gid = fingerprint(event)
            group = self._groups.get(gid)
            if group is None:
                exc = exception_type(event)
                frame = top_app_frame(event.stack)
                group = _Group(gid, exc, frame, f"{event.message.split(chr(10))[0][:100]} ({frame})")
                group.sample_stack = list(event.stack)
                self._groups[gid] = group
            group.timestamps.append(ts)
            group.services.add(event.service)
            if event.message not in group.sample_messages and len(group.sample_messages) < 3:
                group.sample_messages.append(event.message)

    # ---- queries -------------------------------------------------------------------------
    def _last_deploy(self) -> Optional[tuple[datetime, str]]:
        return self._deploys[-1] if self._deploys else None

    def _summary(self, g: _Group, now: datetime, window_start: datetime) -> Optional[GroupSummary]:
        in_window = [t for t in g.timestamps if t >= window_start]
        if not in_window:
            return None
        first, last = min(g.timestamps), max(g.timestamps)
        deploy = self._last_deploy()
        after = bool(deploy and first >= deploy[0])
        return GroupSummary(
            id=g.id, title=g.title, exception=g.exception, top_frame=g.top_frame,
            count=len(in_window), first_seen=first, last_seen=last,
            services=sorted(g.services), urgency=urgency(len(in_window), last, now, after),
            started_after_deploy=after, resolved=g.resolved,
        )

    def list_groups(self, window_minutes: int, min_count: int, include_resolved: bool) -> list[GroupSummary]:
        now = utcnow()
        start = now - timedelta(minutes=window_minutes)
        with self._lock:
            out = [s for g in self._groups.values() if (s := self._summary(g, now, start))]
        out = [s for s in out if s.count >= min_count and (include_resolved or not s.resolved)]
        return sorted(out, key=lambda s: s.urgency, reverse=True)

    def get_group(self, gid: str) -> Optional[GroupDetail]:
        now = utcnow()
        with self._lock:
            g = self._groups.get(gid)
            if g is None:
                return None
            s = self._summary(g, now, datetime.min.replace(tzinfo=timezone.utc))
            deploy = self._last_deploy()
            return GroupDetail(
                **s.model_dump(), sample_messages=list(g.sample_messages),
                sample_stack=list(g.sample_stack), resolved_note=g.resolved_note,
                last_deploy_version=deploy[1] if deploy else None,
                last_deploy_ts=deploy[0] if deploy else None,
            )

    def resolve(self, gid: str, note: str) -> bool:
        with self._lock:
            g = self._groups.get(gid)
            if g is None:
                return False
            g.resolved, g.resolved_note = True, note
            return True

    def deploys(self) -> list[dict]:
        with self._lock:
            return [{"ts": ts, "version": v} for ts, v in self._deploys]


store = Store()
