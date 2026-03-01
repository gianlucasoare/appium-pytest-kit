# Workflow: Test Authoring

## Purpose

Create maintainable tests with high signal and low flake.

## Steps

1. Define behavior under test and category.
2. Choose fixtures/data setup strategy.
3. Use robust selectors and explicit waits.
4. Add assertions for expected state and side effects.
5. Capture diagnostics on failure paths.
6. Classify marker (`smoke`, `regression`, `quarantine`).

## Exit Criteria

- Test is deterministic.
- Failure output is actionable.
- Runtime and scope are appropriate.
