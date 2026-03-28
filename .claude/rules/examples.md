---
description: Rules for example projects
globs:
  - "examples/**"
---

# Example Project Rules

## Purpose
- Examples are the first code users copy — they must work against the current public API
- `examples/basic/` is the minimal smoke test; `examples/my-app/` is the full reference project
- Example collection must pass: `pytest --collect-only examples/basic/tests -q`

## API Usage
- Import only from `appium_pytest_kit` top-level — never from `_internal/`, never from submodules directly
- Use current fixture names: `driver`, `waiter`, `actions`, `page_factory`
- Use current hook names: `pytest_appium_pytest_kit_configure_settings`, `pytest_appium_pytest_kit_capabilities`, `pytest_appium_pytest_kit_driver_created`
- Use `Locator` type alias for all locator tuples
- Page objects must inherit from the scaffolded `BasePage` pattern

## Sync with Framework
- When a fixture is renamed or its return type changes, update all example conftest.py and test files
- When a hook signature changes, update example hook implementations
- When new features ship (soft assertions, data factories, cloud config, locator healing), add usage examples to `examples/my-app/` if they demonstrate a common pattern
- When scaffold output changes (`cli.py` templates), regenerate `examples/my-app/` to match

## Code Quality
- Examples must pass `ruff check examples/`
- No hardcoded credentials, real device UDIDs, or real app package names
- Use descriptive names: `LoginPage`, `AuthFlow`, `test_login_success` — not `Page1`, `flow`, `test_1`
- Comments should explain the "why" for users learning the framework, not the "what"

## conftest.py Patterns
- Show hook usage with realistic capability injection (platform-specific caps, cloud provider integration)
- Show page fixture composition (`login_page`, `home_page` → `logged_in_home`)
- Show flow fixture composition (`auth_flow` → `logged_in`)
- Keep fixture scopes explicit — never rely on pytest defaults
