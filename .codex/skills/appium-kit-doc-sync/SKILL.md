---
name: appium-kit-doc-sync
description: Keep appium-pytest-kit documentation aligned with code. Use when public APIs, fixtures, hooks, settings, CLI behavior, examples, README content, or troubleshooting docs may have drifted after a change or need an audit before release.
---

# Appium Kit Doc Sync

Use live code as the source of truth, then make the docs match it exactly. Prefer small doc fixes in the same patch as the behavior change.

## Audit Order

1. Inspect the code surface that changed.
2. Check the matching doc file.
3. Update examples and README if the surface is user-facing.
4. Verify terminology, defaults, signatures, and env var names match the code.

## Code To Doc Mapping

- `settings.py` -> `docs/configuration.md`
- `pytest_plugin.py` fixtures -> `docs/fixtures.md`
- `hooks.py` -> `docs/conftest-guide.md`
- `errors.py` -> `docs/errors.md`
- `waits.py` -> `docs/waits.md`
- `actions.py` -> `docs/actions.md`
- `cli.py` -> `docs/cli-reference.md`
- `_internal/device_resolver.py` -> `docs/device-resolution.md`
- `_internal/diagnostics.py` -> `docs/diagnostics.md`
- `api.py` -> `docs/api-testing.md`

## Rules

- Document actual names from code, not paraphrases.
- Show settings with field name, `APP_` env var, type, and default.
- Keep examples copy-pastable and aligned with current signatures.
- If a doc entry cannot be verified from code, inspect the source before writing prose.

## Done

- Public behavior and docs agree.
- README and examples do not use stale patterns.
- No changed surface is left undocumented.
