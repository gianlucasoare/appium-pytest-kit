# Playbook: Flaky Test Investigation

## Signals

- Intermittent pass/fail with no code change.
- Retry-required tests rising in flake summaries.

## Procedure

1. Gather `flake-summary.json` and `flake-trend.json`.
2. Identify top failure signatures/locators.
3. Re-run isolated test repeatedly.
4. Remove non-determinism (timing, shared state, unstable selectors).
5. Add deterministic waits/assertions.
6. Decide: fix now or quarantine with owner + expiry.
