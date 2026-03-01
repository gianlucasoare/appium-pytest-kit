# Workflow: Bug Triage And Fix

## Purpose

Resolve defects quickly without introducing regressions.

## Steps

1. Reproduce issue with minimal deterministic case.
2. Isolate failing layer (config, plugin, action, workflow).
3. Add failing unit test that captures bug.
4. Implement minimal fix.
5. Validate with targeted + full unit suite.
6. Add postmortem note if process gap exists.

## Exit Criteria

- Original issue reproduced and fixed.
- Regression test added.
- Related docs updated when behavior changed.
