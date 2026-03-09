# Test Rules

This file applies to `tests/**`.

- Keep one core behavior per test function.
- Do not rely on test execution order or shared mutable state.
- Do not use hard sleeps for synchronization; use explicit waits and deterministic setup.
- Write assertions that reflect user or framework value and produce actionable failure messages.
- Include locator, timeout, and expected-versus-actual detail when a failure path should expose it.
- Use markers intentionally: `smoke`, `regression`, and `quarantine`.
- Give quarantined tests an owner and expiry comment.
- Prefer fixtures for setup and teardown over test-body orchestration.
- Match test file names to the module or surface under test.
- Keep tests safe under `pytest-xdist`.
- Include cleanup when setup creates persistent state.
