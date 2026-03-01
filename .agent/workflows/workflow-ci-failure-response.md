# Workflow: CI Failure Response

## Purpose

Handle CI failures with fast diagnosis and high confidence fixes.

## Steps

1. Identify failing lane and first true error.
2. Classify root cause: flaky test, code regression, environment, workflow config.
3. Reproduce locally with equivalent command.
4. Patch with targeted regression test.
5. Re-run lane-equivalent checks.
6. Capture lessons in ADR or playbook if recurring.

## Exit Criteria

- Root cause confirmed.
- Fix validated in affected lane.
- Recurrence risk reduced.
