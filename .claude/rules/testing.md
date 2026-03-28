---
description: Rules for test files
globs:
  - "tests/**"
---

# Testing Rules

## Structure & Isolation
- One core behavior per test function
- No hidden dependencies on test execution order
- No shared mutable state between test functions
- Tests must be safe under pytest-xdist parallel execution
- Use fixtures for deterministic setup/teardown, not test body logic
- Test file names: `test_<module>.py` matching the module under test
- Include cleanup strategy where setup creates state

## Assertions
- Assertions must reflect user/business value with actionable failure messages
- Failure output must include locator, timeout, and expected vs actual values
- Use `SoftAssert` / `soft_assertions()` when a test validates multiple independent conditions (e.g. form field checks) — fail at the end, not on the first broken field
- `check_equal`, `check_true`, `check_contains` are preferred over raw `sa.check()` for clarity

## Timing
- No hard sleeps as synchronization; use explicit waits and deterministic setup
- In Waiter unit tests, use `default_timeout=0.1, poll_frequency=0.05` for fast execution

## Markers
- Classify tests with markers: `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.quarantine`
- Quarantined tests must have an owner and expiry comment

## Test Data
- Prefer `DataFactory` or standalone generators (`random_email`, `random_username`) over hardcoded test data
- Use seeded `DataFactory(seed=N)` when reproducibility matters for debugging
- Never hardcode credentials or real PII in test data — use generated values

## Mocking Patterns
- Mock the Appium driver with `MagicMock()` for unit tests — never require a real device
- For locator healing tests, use `_mock_driver(*found_locators)` pattern
- For cloud provider tests, use `monkeypatch.setenv()` / `monkeypatch.delenv()` for credentials
- For soft assertion tests, directly instantiate `SoftAssert()` — no driver needed

## Coverage
- Every new public module must have a corresponding `test_<module>.py`
- Coverage gate: `--cov-fail-under=60` (pyproject.toml) — do not lower without discussion
