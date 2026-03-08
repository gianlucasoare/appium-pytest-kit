---
description: Rules for framework source code
globs:
  - "src/appium_pytest_kit/**"
---

# Framework Source Rules

- Backward compatibility: never break public API without deprecation window and migration notes
- Use `wrapper=True` (not deprecated `hookwrapper=True`) for `pytest_runtest_makereport`
- Import `Mapping`, `Iterable`, `Sequence` from `collections.abc`, not `typing`
- Do NOT use `from __future__ import annotations`; exception: `interfaces.py` with `TYPE_CHECKING` guard
- All exceptions must include actionable context (locator, timeout, action attributes)
- All fixtures and hooks must be safe under pytest-xdist parallel execution
- `_internal/` modules are not public API; changes there do not require deprecation
- Public methods must have type hints and deterministic return values
- Never use bare `raise`; always include domain-specific error with context
- Stash key access must use safe existence checks
- New fixtures/helpers require docs update in `docs/` and `README.md`
- Allure integration via soft import only; never add `allure-pytest` as a hard dependency
