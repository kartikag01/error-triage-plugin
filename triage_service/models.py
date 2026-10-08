from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ErrorEvent(BaseModel):
    """One log event. `type="deploy"` events mark releases and are not errors."""

    ts: datetime
    type: Literal["error", "deploy"] = "error"
    service: str = "unknown"
    level: str = "ERROR"
    message: str = ""
    exception: Optional[str] = None  # e.g. "KeyError"; derived from message if absent
    stack: list[str] = Field(default_factory=list)  # "path/file.py:LINE in func"
    version: Optional[str] = None  # for deploy events


class ResolveRequest(BaseModel):
    note: str = ""


class GroupSummary(BaseModel):
    id: str
    title: str
    exception: str
    top_frame: str
    count: int
    first_seen: datetime
    last_seen: datetime
    services: list[str]
    urgency: float
    started_after_deploy: bool
    resolved: bool


class GroupDetail(GroupSummary):
    sample_messages: list[str]
    sample_stack: list[str]
    resolved_note: str = ""
    last_deploy_version: Optional[str] = None
    last_deploy_ts: Optional[datetime] = None
