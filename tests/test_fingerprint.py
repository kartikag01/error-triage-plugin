from datetime import datetime, timezone

from triage_service.fingerprint import fingerprint, normalise_message, top_app_frame
from triage_service.models import ErrorEvent


def ev(message: str, stack: list[str]) -> ErrorEvent:
    return ErrorEvent(ts=datetime.now(timezone.utc), message=message, stack=stack, exception="KeyError")


def test_ids_are_normalised():
    assert normalise_message("order 48213 failed") == normalise_message("order 51907 failed")


def test_library_frames_are_skipped_and_line_numbers_dropped():
    stack = ["site-packages/x/y.py:1 in z", "app/svc.py:88 in build"]
    assert top_app_frame(stack) == "app/svc.py in build"


def test_same_bug_different_ids_same_group():
    stack = ["app/svc.py:9 in build"]
    assert fingerprint(ev("KeyError: 'customer' (order 1)", stack)) == fingerprint(ev("KeyError: 'customer' (order 2)", stack))


def test_different_frames_different_group():
    assert fingerprint(ev("boom", ["a.py:1 in f"])) != fingerprint(ev("boom", ["b.py:1 in f"]))
