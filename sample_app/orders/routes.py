"""Order service. INTENTIONALLY BUGGY: this is the code the agent fixes during the demo."""
from __future__ import annotations


def build_payload(order: dict) -> dict:
    """Build the payload sent to the fulfilment API."""
    return {
        "order_id": order["id"],
        "customer_id": order["customer"]["id"],
        "items": [item["sku"] for item in order["items"]],
    }
