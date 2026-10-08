---
name: error-triage
description: How to prioritise grouped production errors and read stack traces. Use when triaging errors, investigating an incident, deciding what to fix first, or interpreting output from the error-triage MCP tools.
---

# Error triage

## Prioritisation rules (in order)
1. **Started after the latest deploy** (`started_after_deploy = true`) beats everything: it is most likely a regression you can fix.
2. Higher `urgency` score wins. It is `count x (0.5 + recency)` x 1.5 if after deploy.
3. Errors in app code beat errors in third-party calls. Timeouts to an upstream gateway are usually not yours to fix; report them, do not "fix" them with retries.
4. `WARNING`-level groups and one-off blips come last.

## Reading the group
- `top_frame` is the first *application* frame (library frames are skipped, line numbers removed so the group is stable across edits).
- Open the file from `sample_stack[0]` (it has the line number) and read ~20 lines of context.
- See [stack-trace guide](references/stack-trace-guide.md) for common Python exception patterns.

## Report format
```
Top issue: <exception> in <file:function> (<count> in last <window>, started <after deploy vX | before deploy>)
Root cause: <max 3 sentences>
Fix: <what changed>   Test: <test name>   Result: <pass/fail>
Skipped: <group> - <reason>
```

## Do not
- Do not resolve a group without a passing test.
- Do not add broad `try/except` to silence an error. Fix the cause.
