---
name: scaffold
description: Extend the framework with new internal modules, fixtures, page objects, and test files following project conventions.
---

# Scaffold

## Use This Skill When

- Adding a new internal module to `src/appium_pytest_kit/_internal/`
- Creating a new public fixture in `pytest_plugin.py`
- Adding a new page object, flow, or test file to `examples/`
- Extending the CLI scaffolding templates in `cli.py`
- Adding a new error type to `errors.py`

## Scaffold Procedure

1. **Identify what to scaffold**: internal module, fixture, page object, flow, test, error, or CLI template
2. **Check existing patterns**: read the closest existing implementation for conventions
3. **Create the implementation** following the rules below
4. **Add exports** if public: update `__init__.py` with the new class/function/type
5. **Write unit tests** in `tests/unit/test_<module>.py` — one behavior per test
6. **Update documentation** in `docs/` — every public fixture/class/hook needs a doc entry

## Convention Reference

### Internal modules (`_internal/`)
- Frozen dataclasses for value objects (`@dataclass(frozen=True, slots=True)`)
- Type hints on all public methods
- Domain-specific errors with context attributes (`.locator`, `.timeout`, `.action`)
- Soft optional imports (`try: import yaml except ImportError: yaml = None`)
- No `from __future__ import annotations`

### Fixtures (`pytest_plugin.py`)
- Use `pytest.Config.stash` with typed `StashKey` for state
- Choose scope carefully: `session` for shared resources, `function` for per-test
- Must be xdist-safe (no shared mutable state across workers)
- Register new stash keys at module level: `MY_KEY: StashKey[Type] = StashKey()`
- Add teardown via `yield` or `request.addfinalizer`

### Page objects (`examples/my-app/pages/`)
- Inherit from `BasePage`
- Locators as class-level `Locator` tuples: `ELEMENT = (MobileBy.ID, "com.app:id/element")`
- Methods return `self` for chaining or a value for queries
- No waits in `__init__` — use `is_loaded()` pattern

### Test files
- File name: `test_<module>.py`
- One core behavior per test function
- Markers: `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.quarantine`
- Fixtures for setup/teardown, not test body logic
- Assertions with actionable failure messages

### Errors (`errors.py`)
- Inherit from `AppiumPytestKitError`
- Add context attributes and set them in `__init__`
- Include the context in the error message string

### CLI templates (`cli.py`)
- Template strings as module-level constants (e.g., `_MY_TEMPLATE = """\n...\n"""`)
- Write files via `_write_file()` helper
- Update `--framework` scaffold if adding new directories/files

## Rules

- Always check for existing patterns before creating new ones
- Internal modules (`_internal/`) are not public API — no deprecation needed for changes
- Public modules need backward-compatible additions only
- Import `Mapping`, `Iterable`, `Sequence` from `collections.abc`
- Never use `from __future__ import annotations`

## Definition of Done

- Implementation follows project conventions
- Unit tests cover the new behavior
- Exports updated in `__init__.py` if public
- Documentation added to `docs/`
- `python3 -m ruff check .` passes
- `python3 -m pytest -q` passes
