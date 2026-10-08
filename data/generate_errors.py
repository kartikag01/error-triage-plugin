"""Generate synthetic errors.jsonl (deterministic). No real or client data.

Story told by the data (relative to "now", so the demo window always works):
  * deploy v2.4.1 happened 95 minutes ago
  * KeyError 'customer' in orders/service.py starts right after it  -> the real bug
  * payment gateway timeouts are noisy but pre-date the deploy        -> upstream flakiness
  * a handful of invalid-quantity errors and one cache blip           -> low priority
"""
from __future__ import annotations

import json
import random
from pathlib import Path

random.seed(42)
OUT = Path(__file__).with_name("errors.jsonl")
LIB = "site-packages/fastapi/routing.py:214 in app"

events: list[dict] = [{"type": "deploy", "minutes_ago": 95, "service": "orders-api", "version": "v2.4.1"}]

# 1) The bug: guest checkout orders have no "customer" key (started after the deploy)
for _ in range(214):
    events.append({
        "type": "error", "minutes_ago": round(random.uniform(1, 90), 1), "service": "orders-api",
        "level": "ERROR", "exception": "KeyError",
        "message": f"KeyError: 'customer' (order {random.randint(40000, 59999)})",
        "stack": ["sample_app/orders/service.py:9 in build_payload",
                  "sample_app/orders/routes.py:7 in create_order", LIB],
    })

# 2) Noise: payment gateway timeouts, before and after the deploy
for _ in range(38):
    events.append({
        "type": "error", "minutes_ago": round(random.uniform(1, 180), 1), "service": "payments-api",
        "level": "ERROR", "exception": "TimeoutError",
        "message": "TimeoutError: payment gateway timed out after 30s",
        "stack": ["sample_app/payments/client.py:6 in charge", LIB],
    })

# 3) Low priority: bad quantities
for _ in range(6):
    events.append({
        "type": "error", "minutes_ago": round(random.uniform(5, 150), 1), "service": "inventory-api",
        "level": "WARNING", "exception": "ValueError",
        "message": f"ValueError: invalid quantity {random.choice([0, -1, -3])} for sku SKU-{random.randint(100, 999)}",
        "stack": ["sample_app/inventory/stock.py:6 in reserve", LIB],
    })

# 4) One-off blip
events.append({
    "type": "error", "minutes_ago": 22.0, "service": "orders-api", "level": "ERROR",
    "exception": "ConnectionResetError", "message": "ConnectionResetError: cache connection reset by peer",
    "stack": ["sample_app/cache/redis_client.py:31 in get", LIB],
})

events.sort(key=lambda e: -e["minutes_ago"])
OUT.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
print(f"wrote {len(events)} events to {OUT}")
