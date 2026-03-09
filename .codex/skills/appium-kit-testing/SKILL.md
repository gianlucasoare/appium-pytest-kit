---
name: appium-kit-testing
description: Design and extend reliable automated tests and fixtures for appium-pytest-kit. Use when adding coverage, creating or refactoring pytest fixtures, improving failure diagnostics, classifying tests, or making tests safe for xdist and retry-heavy automation.
---

# Appium Kit Testing

Build deterministic tests and fixtures that remain readable under CI pressure. Use the current tests and plugin code as the pattern library.

## Test Design

1. Start from the behavior or failure path that matters most.
2. Choose the narrowest level that proves it: unit helper, fixture behavior, plugin hook, CLI path, or example collection.
3. Keep one core behavior per test and make assertions explain the value of the failure.
4. Use explicit waits and deterministic setup instead of sleeps or order dependence.
5. Mark the test appropriately: `smoke`, `regression`, or `quarantine`.

## Fixture Design

1. Define the resource lifecycle before writing code.
2. Choose scope intentionally: prefer `function`, use broader scopes only when the resource is safe and worth sharing.
3. Store shared state in `pytest.Config.stash` with typed keys, not globals.
4. Design teardown for partial setup failures, especially around drivers, processes, and temp artifacts.
5. Check xdist safety and retry behavior before treating the fixture as done.

## Repo-Specific Checks

- For framework fixtures, inspect `src/appium_pytest_kit/pytest_plugin.py` first.
- For action or waiter behavior, mirror the existing style in `tests/unit/test_actions_expanded*.py` and `tests/unit/test_waits_expanded*.py`.
- If a new fixture or public helper is added, update `docs/fixtures.md` or the matching docs file in the same change.
- If a flaky test cannot be stabilized quickly, prefer quarantine with owner and expiry rather than hiding the signal.

## Done

- Tests are deterministic and xdist-safe.
- Failure output is actionable.
- Setup and cleanup are explicit.
- Documentation changes ship with new public test surfaces.
