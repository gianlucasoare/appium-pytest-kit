---
name: debug
description: Skill for systematic debugging: isolate failures, reproduce deterministically, identify root cause, and land regression-safe fixes.
---

# Debug

## Use This Skill When

- A test, workflow, or runtime path is failing.
- Behavior is flaky, intermittent, or environment-sensitive.
- You need root-cause analysis before patching.

## Debug Loop

1. Capture the first real error and full context.
2. Reproduce with the smallest deterministic command.
3. Narrow scope (binary search on code path/config/data).
4. Form one hypothesis at a time and validate quickly.
5. Implement minimal fix at the true fault boundary.
6. Add/adjust regression test to lock behavior.
7. Re-run impacted lane, then full quality checks.

## Rules

- Do not patch on symptoms only.
- Avoid broad catch-all fixes that hide signal.
- Keep debug instrumentation temporary and removable.
- Preserve unrelated behavior and existing contracts.

## Deliverables

- Root cause summary (what failed and why).
- Fix summary (what changed and where).
- Regression proof (tests/commands that now pass).
