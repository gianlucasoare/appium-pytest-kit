---
description: Rules for test files
globs:
  - "tests/**"
---

# Testing Rules

- One core behavior per test function
- No hidden dependencies on test execution order
- No hard sleeps as synchronization; use explicit waits and deterministic setup
- Assertions must reflect user/business value with actionable failure messages
- Failure output must include locator, timeout, and expected vs actual values
- Classify tests with markers: `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.quarantine`
- Quarantined tests must have an owner and expiry comment
- Include cleanup strategy where setup creates state
- Use fixtures for deterministic setup/teardown, not test body logic
- Test file names: `test_<module>.py` matching the module under test
- Tests must be safe under pytest-xdist parallel execution
- No shared mutable state between test functions
