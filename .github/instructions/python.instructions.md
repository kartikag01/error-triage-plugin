---
applyTo: "**/*.py"
---
- Prefer small pure functions; keep FastAPI route handlers thin and put logic in `store.py` / `fingerprint.py` / `scoring.py`.
- Use `from __future__ import annotations` and typed signatures.
- No broad `except Exception: pass`. Handle specific errors or let them surface.
- Tests: one behaviour per test, descriptive names, no network.
