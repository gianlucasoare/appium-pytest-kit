---
name: appium-kit-doc-checker
description: Compare appium-pytest-kit documentation against the live codebase. Use when auditing exported APIs, fixtures, hooks, settings, errors, CLI options, examples, or docs coverage for missing, stale, or incomplete documentation.
---

# Appium Kit Doc Checker

Audit docs against code systematically and report each gap by type.

## Audit Procedure

1. Inspect current exports in `src/appium_pytest_kit/__init__.py`.
2. Inspect the live source for settings, fixtures, hooks, errors, waits, actions, CLI, and examples.
3. Compare each surface to the matching doc file.
4. Classify each gap as `MISSING`, `STALE`, or `INCOMPLETE`.

## Mapping

- Settings -> `docs/configuration.md`
- Fixtures -> `docs/fixtures.md`
- Hooks -> `docs/conftest-guide.md`
- Errors -> `docs/errors.md`
- Waits -> `docs/waits.md`
- Actions -> `docs/actions.md`
- CLI -> `docs/cli-reference.md`
- Device resolution -> `docs/device-resolution.md`
- Diagnostics -> `docs/diagnostics.md`
- API client -> `docs/api-testing.md`

## Output

- Summarize each area with status and gap count.
- List every gap with the specific code surface and doc file.
- Prioritize `MISSING` before `STALE`, and `STALE` before `INCOMPLETE`.
