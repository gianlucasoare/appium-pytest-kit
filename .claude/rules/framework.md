---
description: Rules for framework source code
globs:
  - "src/appium_pytest_kit/**"
---

# Framework Source Rules

## Public API & Compatibility
- Backward compatibility: never break public API without deprecation window and migration notes
- `__init__.py` is the single source of truth for public exports — update it for every new public class/function
- `_internal/` modules are not public API; changes there do not require deprecation

## Coding Standards
- Use `wrapper=True` (not deprecated `hookwrapper=True`) for `pytest_runtest_makereport`
- Import `Mapping`, `Iterable`, `Sequence` from `collections.abc`, not `typing`
- Do NOT use `from __future__ import annotations`; exception: `interfaces.py` with `TYPE_CHECKING` guard
- Public methods must have type hints and deterministic return values
- Code must pass `ruff check .` and `mypy src/appium_pytest_kit/`

## Error Handling
- All exceptions must inherit from `AppiumPytestKitError`
- All exceptions must include actionable context attributes (`.locator`, `.timeout`, `.action`, `.failures`, `.method`, `.url`, `.status_code`, `.diff_ratio`, `.threshold` as appropriate)
- Never use bare `raise`; always include domain-specific error with context
- `SoftAssertionError` carries `.failures` list and `.failure_count`

## Optional Dependencies
- Allure integration via soft import only; never add `allure-pytest` as a hard dependency
- Pillow (`visual.py`) via soft import; guarded by `try/except ImportError`
- PyYAML (`parametrize.py`, `_internal/device_resolver.py`) via soft import
- Any new optional dep must use `try/except ImportError` with a clear install hint message

## Cloud & Credentials
- Cloud provider credentials (`BROWSERSTACK_*`, `SAUCE_*`, `AWS_*`) must only come from environment variables
- Never hardcode cloud URLs, tokens, or API keys in source code
- `cloud.py` adapters raise `ConfigurationError` with the missing env var name

## Locator Healing
- `LocatorChain` fallbacks are tried in declared order; primary first
- Healing events are logged at WARNING level for visibility
- `HealingRegistry` tracks statistics but never mutates test behavior

## State & Safety
- All fixtures and hooks must be safe under pytest-xdist parallel execution
- Stash key access must use safe existence checks
- `DataFactory` must be stateless across tests when unseeded; seeded mode uses per-instance RNG
- `SoftAssert` must not leak state between `assert_all()` calls (auto-resets after raise)

## Documentation
- New fixtures/helpers/modules require docs update in `docs/` and `README.md`
- New public modules require entry in `.claude/agents/` and `.claude/skills/` where they maintain inventories
