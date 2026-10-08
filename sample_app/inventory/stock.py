from __future__ import annotations


def reserve(sku: str, qty: int) -> int:
    if qty <= 0:
        raise ValueError(f"invalid quantity {qty} for sku {sku}")
    return qty
