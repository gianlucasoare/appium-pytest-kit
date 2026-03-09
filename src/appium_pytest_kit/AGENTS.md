# Source Rules

This file applies to `src/appium_pytest_kit/**`.

- Preserve backward compatibility for public APIs unless the change explicitly includes deprecation, migration notes, and matching version semantics.
- Use `wrapper=True` for `pytest_runtest_makereport`; do not introduce deprecated `hookwrapper=True`.
- Import `Mapping`, `Iterable`, and `Sequence` from `collections.abc`, not `typing`.
- Do not add `from __future__ import annotations`; keep the existing exception pattern only where already present.
- Include actionable context on framework exceptions so callers can see locator, timeout, action, or equivalent failure data.
- Keep fixtures, hooks, and reporting code safe under `pytest-xdist`.
- Treat `_internal/` modules as non-public; they can change without deprecation, but public modules cannot.
- Keep public methods typed and deterministic.
- Avoid bare `raise` and generic error wrapping that drops domain context.
- Use safe stash key existence checks.
- Update `README.md` and the relevant `docs/` entry when adding or changing public fixtures, helpers, settings, CLI behavior, or hooks.
- Keep Allure support optional via soft import only.
