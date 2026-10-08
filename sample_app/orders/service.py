"""Order service."""
from __future__ import annotations


def build_payload(order: dict) -> dict:
    """Build the payload sent to the fulfilment API.

    Guest checkout orders do not include a customer object, so the customer_id
    field is only added when it is actually present.
    """
    payload = {
        "order_id": order["id"],
        "items": [item["sku"] for item in order.get("items", [])],
    }

    customer = order.get("customer")
    if customer is not None and "id" in customer:
        payload["customer_id"] = customer["id"]

    return payload
