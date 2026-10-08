# Stack trace guide (Python)

| Exception | Usual cause | First thing to check |
|---|---|---|
| `KeyError: 'x'` | Dict missing a key (often an optional field, e.g. guest users) | Where the dict is built; is `x` optional upstream? Use `.get()` with an explicit default or validate earlier |
| `TypeError: 'NoneType' object is not subscriptable` | A value that can be `None` is indexed | The line above; where does the `None` come from? |
| `AttributeError: 'NoneType' ...` | Same as above, attribute access | Same |
| `TimeoutError` / `ConnectionResetError` | Upstream or network | Not usually an app bug; check whether it pre-dates the deploy |
| `ValueError` | Input validation | Is bad input coming from users (expected) or from our own code (bug)? |

Read traces **bottom-up for the cause, top-down for the path**. Skip frames from `site-packages`.
