from __future__ import annotations


def charge(amount: float, timeout: int = 30) -> dict:
    """Calls the (flaky) payment gateway. Timeouts here are upstream noise."""
    raise TimeoutError(f"payment gateway timed out after {timeout}s")
