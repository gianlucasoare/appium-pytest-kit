---
name: debug
description: Systematic debugging from reproduction through root cause to regression-safe fix, including bug triage workflow.
---

# Debug

## Use This Skill When

- A test, workflow, or runtime path is failing
- Behavior is flaky, intermittent, or environment-sensitive
- You need root-cause analysis before patching
- Triaging a bug report to resolution

## Debug Loop

1. Capture the first real error and full context (not the final summary line)
2. Reproduce with the smallest deterministic command
3. Narrow scope — binary search on code path, config, or data
4. Form one hypothesis at a time and validate quickly
5. Implement minimal fix at the true fault boundary
6. Add or adjust a regression test to lock behavior
7. Re-run impacted lane, then full quality checks

## Bug Triage Procedure

1. Reproduce issue with minimal deterministic case
2. Isolate failing layer: config, plugin, action, or workflow
3. Add a failing unit test that captures the bug
4. Implement minimal fix
5. Validate with targeted test + full unit suite
6. Add postmortem note if a process gap exists

## Rules

- Do not patch on symptoms only
- Avoid broad catch-all fixes that hide signal
- Keep debug instrumentation temporary and removable
- Preserve unrelated behavior and existing contracts
- Start from the first real traceback, not the final summary

## Definition of Done

- Original issue reproduced and fixed
- Regression test added and passing
- Related docs updated when behavior changed
- Root cause summary documented (what failed and why)
