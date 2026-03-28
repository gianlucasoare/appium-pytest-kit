# appium-pytest-kit

## Package Identity

- PyPI: `appium-pytest-kit`
- Import: `appium_pytest_kit` (src layout: `src/appium_pytest_kit/`)
- CLI: `appium-pytest-kit-init`, `appium-pytest-kit-doctor`
- pytest11 entry point: `appium-pytest-kit = "appium_pytest_kit.pytest_plugin"`
- GitHub: https://github.com/gianlucasoare/appium-pytest-kit
- Python: >=3.11

## Dev Workflow

```bash
python3 -m pip install -e ".[dev]"          # install with dev extras
python3 -m ruff check .                     # lint
python3 -m pytest -q                        # unit tests (testpaths: tests/unit)
python3 -m pytest --collect-only examples/basic/tests -q  # example collection
```

### CI-Style Lanes

```bash
python3 -m pytest -q -m "not quarantine"              # main lane
python3 -m pytest -q -m quarantine                     # quarantine lane
python3 -m pytest -q -n 2 -m "not quarantine"          # xdist sanity lane
```

### Quality Gate Scripts

```bash
python3 scripts/check_flake_thresholds.py \
  --summary artifacts/appium-pytest-kit/flake-summary.json \
  --trend artifacts/appium-pytest-kit/flake-trend.json
python3 scripts/check_perf_thresholds.py \
  --summary artifacts/appium-pytest-kit/perf-summary.json \
  --trend artifacts/appium-pytest-kit/perf-trend.json
```

## Release Preflight (Mandatory)

Before any PyPI push or release tag, all steps must pass:

1. `python3 -m ruff check .`
2. `python3 -m pytest -q`
3. `python3 -m pytest -q -n 2 -m "not quarantine"`
4. `python3 -m build`
5. `python3 -m twine check dist/*`

If any step fails, release is blocked. After release: verify PyPI version, GitHub release notes, install smoke test (`pip install appium-pytest-kit==X.Y.Z`).

## Architecture

- **src layout** with `_internal/` for non-public modules: `device_resolver.py`, `diagnostics.py`, `video.py`, `server.py`, `reporting.py`
- **Public modules**: `actions.py`, `api.py`, `cloud.py`, `driver.py`, `errors.py`, `hooks.py`, `interfaces.py`, `locator_healing.py`, `parametrize.py`, `settings.py`, `soft_assertions.py`, `test_data.py`, `visual.py`, `waits.py`
- **Stash keys**: `SETTINGS_KEY`, `REPORTER_KEY`, `DRIVER_KEY`, `RECORDER_KEY`, `DEVICE_INFO_KEY`
- **Settings**: `AppiumPytestKitSettings` (env prefix `APP_`)
- **Base error**: `AppiumPytestKitError`
- **Error hierarchy**: `ConfigurationError`, `DeviceResolutionError`, `LaunchValidationError`, `WaitTimeoutError`, `ActionError`, `DriverCreationError`, `ApiRequestError`, `VisualRegressionError`, `SoftAssertionError`
- **Hook specs class**: `AppiumPytestKitHookSpecs`
- **Hooks**: `pytest_appium_pytest_kit_configure_settings`, `pytest_appium_pytest_kit_capabilities`, `pytest_appium_pytest_kit_driver_created`
- **Cloud providers**: `build_cloud_config()` for BrowserStack, Sauce Labs, AWS Device Farm
- **Locator healing**: `LocatorChain`, `HealingRegistry`, `chain()` shorthand
- **Soft assertions**: `SoftAssert`, `soft_assertions()` context manager
- **Test data**: `DataFactory` with seedable randomness, standalone generators

## Coding Conventions

- Do NOT use `from __future__ import annotations` (Python 3.11+ only); only `interfaces.py` uses it behind `TYPE_CHECKING` guard
- Import `Mapping`, `Iterable`, `Sequence` from `collections.abc`, not `typing`
- Use `wrapper=True` (not deprecated `hookwrapper=True`) for `pytest_runtest_makereport`
- Raise domain-specific errors with context: `WaitTimeoutError`, `ActionError` carry `.locator`, `.timeout`, `.action`; `SoftAssertionError` carries `.failures`, `.failure_count`; `ApiRequestError` carries `.method`, `.url`, `.status_code`; `VisualRegressionError` carries `.baseline_path`, `.actual_path`, `.diff_ratio`, `.threshold`
- Type hints on all public interfaces; no dead code or commented-out blocks
- Allure integration via soft import, no hard dependency

## Change Protocol

- **Patch**: bug fixes, no API/behavior break
- **Minor**: backward-compatible features
- **Major**: breaking behavior or API change — requires migration notes + deprecation window
- Every change: tests proving new + unchanged behavior, docs updated, quality gates pass
- Architecture-impacting changes require ADR in `docs/decisions/`
- If scaffold output changes, update project-structure and CLI docs in the same change set

## Operational Rules

- **CI failure handling**: start from first real traceback, reproduce locally, add regression test, re-run impacted lane then full suite
- **xdist-safe reporting**: never assume report files exist per worker, safe existence checks, idempotent merge logic, separate controller/worker responsibilities
- **Security**: never store tokens in source files/docs/issues, use env vars for secrets, rotate exposed tokens immediately
- **Docs ship with behavior**: any new fixture/helper/CLI behavior requires README update + docs/ update
- **Publish verification**: verify PyPI version, GitHub release notes, install + import smoke after every release

## Guidance Sync Policy

- `CLAUDE.md` and `AGENTS.md` should stay semantically aligned on repo-wide policy, commands, release gates, and architectural constraints.
- Update both root guidance files when a shared rule changes, even if only one assistant currently depends on the wording.
- Keep assistant-specific discovery details separate: Claude skill and rule routing belongs in `.claude/`, while Codex skill routing belongs in `AGENTS.md` and `.codex/skills/`.
- If the two systems ever disagree, treat that as maintenance drift and reconcile the rule before relying on it.
