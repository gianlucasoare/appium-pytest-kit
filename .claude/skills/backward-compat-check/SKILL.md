---
name: backward-compat-check
description: Verify changes preserve public API and backward compatibility before merge or release.
---

# Backward Compatibility Check

## Use This Skill When

- Preparing a PR that touches public modules
- Before tagging a release
- After refactoring public classes, functions, or fixtures
- When changing hook signatures or fixture return types
- When modifying `AppiumPytestKitSettings` fields

## Check Procedure

1. **Identify public API surface**: read `src/appium_pytest_kit/__init__.py` for all exports
2. **Diff against previous**: compare current exports with the last release tag
3. **Classify changes** using the change protocol:
   - **Patch**: bug fixes, no API/behavior break
   - **Minor**: backward-compatible additions (new exports, new optional settings fields)
   - **Major**: breaking changes (removed exports, changed signatures, renamed settings)
4. **Check fixtures**: verify all fixture names, scopes, and return types are preserved
5. **Check hooks**: verify hook signatures haven't changed
6. **Check settings**: verify no `APP_*` env vars were removed or had their types changed
7. **Check errors**: verify exception class names and attribute names are preserved
8. **Check CLI**: verify CLI flags and their behavior are preserved
9. **Report findings**: list all changes categorized by severity

## Public API Surface

### Exports (`__init__.py`)
```
ActionError, ApiClient, ApiResponse, AppiumPytestKitError,
AppiumPytestKitSettings, ConfigurationError, DeviceInfo,
DeviceResolutionError, DriverConfig, DriverCreationError,
LaunchValidationError, Locator, MobileActions, WaitTimeoutError,
Waiter, __version__, apply_cli_overrides, build_driver_config,
create_driver, load_settings
```

### Fixtures
```
settings, device_info, appium_server, driver, waiter, actions, page_factory
```

### Hooks
```
pytest_appium_pytest_kit_configure_settings(settings) -> Settings | None
pytest_appium_pytest_kit_capabilities(capabilities, settings) -> Mapping | None
pytest_appium_pytest_kit_driver_created(driver, settings) -> None
```

### CLI commands
```
appium-pytest-kit-init [--framework] [--root PATH] [--force] [--install-extras EXTRAS]
appium-pytest-kit-doctor [--env-file PATH] [--json]
```

## Breaking Change Rules

- Removing an export from `__init__.py` is a **major** change
- Changing a fixture name, scope, or return type is a **major** change
- Changing a hook signature is a **major** change
- Removing or renaming an `APP_*` setting is a **major** change
- Changing default values for existing settings is a **minor** change (document it)
- Adding new optional settings fields is a **minor** change
- Adding new exports is a **minor** change
- Changes to `_internal/` modules are **patch** level (not public API)

## If Breaking Changes Are Necessary

1. Document the change in an ADR in `docs/decisions/`
2. Add deprecation warnings in the current release
3. Provide migration notes in the changelog
4. Bump major version
5. Update all examples and documentation

## Definition of Done

- All changes classified as patch, minor, or major
- No unintentional breaking changes
- Version bump matches the highest severity change
- Migration notes written for any breaking changes
- Examples updated to use new API if changed
