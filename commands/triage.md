---
description: Triage recent production errors and fix the most urgent one
argument-hint: "[look-back window in minutes, default 120]"
agent: triage-oncall
---

Triage production errors from the last ${input:window:120} minutes (arguments: $ARGUMENTS).

1. List the error groups and rank them by urgency.
2. For the top group, fetch the details and find the failing code in this workspace.
3. Explain the root cause in 3 sentences or fewer.
4. Propose a minimal fix and **wait for my approval** before editing anything.
5. Add a regression test and run it.
6. If the tests pass, mark the group resolved.
7. List any groups you skipped and why.
