---
name: flaky-test-investigation
description: Investigate and resolve flaky tests using telemetry data, isolation, and deterministic stabilization.
---

# Flaky Test Investigation

## Use This Skill When

- Tests intermittently pass/fail with no code change
- Retry-required tests are rising in flake summaries
- Investigating non-deterministic behavior in CI

## Procedure

1. Gather `flake-summary.json` and `flake-trend.json` from artifacts
2. Identify top failure signatures and locators
3. Re-run the isolated test repeatedly to confirm flakiness
4. Remove non-determinism: timing, shared state, unstable selectors
5. Add deterministic waits and assertions
6. Decide: fix now or quarantine with owner + expiry

## Quarantine Rules

- Quarantined tests must have `@pytest.mark.quarantine`
- Each must have an owner and an expiry date comment
- Quarantine lane runs separately: `python3 -m pytest -q -m quarantine`
- Review and reduce quarantine count weekly

## Common Causes

- Hard sleeps instead of explicit waits
- Shared mutable state between tests
- Unstable element selectors
- Race conditions in async operations
- Environment-dependent behavior

## Definition of Done

- Flaky behavior root-caused
- Either stabilized with deterministic fix or quarantined with owner + expiry
- Flake summary trend improving
