---
name: regression-test
description: How to write a minimal pytest regression test for a fixed bug. Use after applying an error fix, when asked to add a test, or before marking an error group resolved.
---

# Regression test for a fixed bug

1. Put the test next to the existing tests for that module (e.g. `sample_app/tests/test_service.py`).
2. Name it after the behaviour: `test_guest_checkout_payload_has_no_customer_id`, not `test_fix_123`.
3. Reproduce the **exact input** from the error (use the sample message / stack to rebuild it).
4. Assert the corrected behaviour, not just "does not raise".
5. Run it **before** the fix if practical (it should fail), then after (it should pass).
6. Run the whole module's tests, not only the new one.

Keep it to ~10 lines. No mocks unless the code under test calls the network.
