"""Fingerprinting: collapse many raw errors into a few groups.

fingerprint = hash(exception type + first *app* frame (no line number) + normalised message)
"""
from __future__ import annotations

import hashlib
import re

from .models import ErrorEvent

_LIB_MARKERS = ("site-packages", "dist-packages", "/usr/lib", "<frozen", "asyncio/", "threading.py")
_UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
_HEX = re.compile(r"\b0x[0-9a-fA-F]+\b")
_NUM = re.compile(r"\d+")


def exception_type(event: ErrorEvent) -> str:
    if event.exception:
        return event.exception
    head = event.message.split(":", 1)[0].strip()
    return head if head and " " not in head else "Error"


def top_app_frame(stack: list[str]) -> str:
    """First frame that is app code, with the line number removed (stable across edits)."""
    for frame in stack:
        if not any(marker in frame for marker in _LIB_MARKERS):
            location, _, func = frame.partition(" in ")
            path = location.rsplit(":", 1)[0]
            return f"{path} in {func}".strip() if func else path
    return stack[0].rsplit(":", 1)[0] if stack else "unknown"


def normalise_message(message: str) -> str:
    msg = _UUID.sub("<uuid>", message)
    msg = _HEX.sub("<hex>", msg)
    msg = _NUM.sub("<n>", msg)
    return msg.strip()


def fingerprint(event: ErrorEvent) -> str:
    raw = "|".join([exception_type(event), top_app_frame(event.stack), normalise_message(event.message)])
    return hashlib.sha1(raw.encode()).hexdigest()[:12]
