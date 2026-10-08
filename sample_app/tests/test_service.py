from sample_app.orders.service import build_payload


def test_registered_customer_payload():
    order = {"id": 1, "customer": {"id": 7}, "items": [{"sku": "A1"}]}
    assert build_payload(order) == {"order_id": 1, "customer_id": 7, "items": ["A1"]}
