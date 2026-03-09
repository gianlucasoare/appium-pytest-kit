---
name: dependency-audit
description: Audit, add, update, and manage project dependencies across required and optional extras groups.
---

# Dependency Audit

## Use This Skill When

- Adding or removing a dependency
- Updating dependency version bounds
- Checking for outdated or vulnerable packages
- Managing extras groups (yaml, allure, retry, xdist, all, dev)
- Investigating dependency conflicts or resolution failures

## Audit Procedure

1. **Read current state**: parse `pyproject.toml` for all dependency specs
2. **Check installed versions**: `pip list --format=json` for actual installed versions
3. **Check for outdated**: `pip list --outdated --format=json`
4. **Verify compatibility**: ensure all deps support Python >=3.11
5. **Review bounds**: check that version bounds are not over-constrained or under-constrained
6. **Cross-reference usage**: grep imports to verify each dependency is actually used
7. **Check extras**: verify each extras group installs cleanly

## Dependency Groups

| Group | Dependencies | Purpose |
|-------|-------------|---------|
| required | `Appium-Python-Client>=4.0.0`, `pydantic-settings>=2.3.0`, `pytest>=8.2.0` | Core framework |
| `[yaml]` | `PyYAML>=6.0` | Device profile loading |
| `[allure]` | `allure-pytest>=2.13.0` | Allure report integration |
| `[retry]` | `pytest-retry>=0.6.0` | Flaky test retry |
| `[xdist]` | `pytest-xdist>=3.6.0` | Parallel execution |
| `[all]` | All optional extras | Everything |
| `[dev]` | `ruff>=0.9.0`, `pytest-cov>=6.0.0` | Development tools |

## Adding a Dependency

1. Determine if it's required or optional
2. If optional: which extras group? Create a new one if it doesn't fit existing groups
3. Add to `pyproject.toml` with minimum version bound (e.g., `>=X.Y.Z`)
4. If optional: use soft import pattern in code:
   ```python
   try:
       import new_dep
   except ImportError:
       new_dep = None
   ```
5. Update `[all]` extras if adding a new optional group
6. Add to `docs/installation.md` with install command

## Version Bound Rules

- Use `>=X.Y.Z` for minimum bounds (not `==` or `~=`)
- Only add upper bounds (`<X.0.0`) when there's a known incompatibility
- Core deps (Appium-Python-Client, pydantic-settings, pytest) should track latest stable
- Dev deps can be more aggressive with minimum versions

## Rules

- Never add a hard dependency for optional functionality — use soft imports
- Every dependency must have at least one import in the codebase
- Optional deps must degrade gracefully when not installed
- Test with and without optional extras: `pip install -e .` vs `pip install -e ".[all]"`
- Never pin exact versions in library packages (only in applications)
- Document new dependencies in `docs/installation.md`

## Definition of Done

- `pyproject.toml` updated with correct bounds
- Soft import pattern used for optional deps
- Code works without optional dep installed
- `pip install -e ".[dev]"` succeeds
- `python3 -m ruff check .` passes
- `python3 -m pytest -q` passes
