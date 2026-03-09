---
name: appium-kit-coverage-analyzer
description: Analyze coverage gaps in appium-pytest-kit by comparing source modules against tests and collected cases. Use when planning new tests, auditing under-tested modules, or prioritizing missing edge-case and failure-path coverage before refactors or releases.
---

# Appium Kit Coverage Analyzer

Use the current codebase as the map, then identify the highest-value missing tests.

## Procedure

1. Inventory source modules under `src/appium_pytest_kit/`.
2. Inventory unit tests under `tests/unit/test_*.py`.
3. Map each source module to the most relevant test file or files.
4. Inspect public methods and key failure branches in the source.
5. Grep for test references and run collection when needed.
6. Prioritize gaps by risk, not by raw file count.

## Current Mapping Hints

- `settings.py` -> `test_settings.py`, `test_session_settings.py`
- `waits.py` -> `test_waits_expanded.py`, `test_waits_expanded2.py`
- `actions.py` -> `test_actions_expanded.py`, `test_actions_expanded2.py`
- `driver.py` -> `test_driver_config.py`
- `cli.py` -> `test_cli.py`, `test_cli_doctor.py`, `test_cli_scaffold.py`
- `pytest_plugin.py` -> `test_pytest_plugin.py`
- `_internal/device_resolver.py` -> `test_device_resolver.py`
- `_internal/diagnostics.py` -> `test_diagnostics.py`
- `_internal/server.py` -> `test_server.py`

Treat `_internal/video.py` and `_internal/reporting.py` as high-interest files when they have no dedicated coverage.

## Coverage Priorities

- Public methods not referenced by tests.
- Error handling and boundary conditions.
- Optional dependency branches.
- xdist controller versus worker logic.
- CLI and scaffold paths that could drift silently.

## Output

- Summarize each module as well-covered, partially covered, under-tested, or untested.
- List the highest-value missing tests first.
