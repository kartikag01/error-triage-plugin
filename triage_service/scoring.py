"""Urgency score. Deliberately simple so you can explain it on a slide.

urgency = count * (0.5 + recency) * (1.5 if started after the latest deploy else 1)
recency = 0.5 ** (minutes since last seen / 30)   -> 1.0 now, 0.5 after 30 min, ...
"""
from __future__ import annotations

from datetime import datetime


def recency_weight(last_seen: datetime, now: datetime) -> float:
    minutes = max((now - last_seen).total_seconds() / 60.0, 0.0)
    return 0.5 ** (minutes / 30.0)


def urgency(count: int, last_seen: datetime, now: datetime, started_after_deploy: bool) -> float:
    score = count * (0.5 + recency_weight(last_seen, now))
    if started_after_deploy:
        score *= 1.5
    return round(score, 1)
