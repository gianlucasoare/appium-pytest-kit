# Contributing to appium-pytest-kit

Thanks for your interest in contributing! This guide covers everything you need to get started.

## Setup

```bash
git clone https://github.com/gianlucasoare/appium-pytest-kit.git
cd appium-pytest-kit
python3 -m pip install -e ".[dev]"
```

To install all optional extras (yaml, allure, retry, xdist):

```bash
python3 -m pip install -e ".[dev,all]"
```

## Running checks

All three must pass before submitting a PR:

```bash
python3 -m ruff check .                          # lint
python3 -m mypy src/appium_pytest_kit/            # type check
python3 -m pytest -q                              # unit tests (with coverage gate)
```

### CI lanes

```bash
python3 -m pytest -q -m "not quarantine"          # main lane
python3 -m pytest -q -m quarantine                # quarantine lane
python3 -m pytest -q -n 2 -m "not quarantine"     # xdist sanity (requires: pip install -e ".[dev,xdist]")
```

## Code style

- **Linter**: ruff (config in `pyproject.toml`)
- **Type checker**: mypy (`--check-untyped-defs`, `--ignore-missing-imports`)
- **Python**: 3.11+ only. Do **not** use `from __future__ import annotations`
- Import `Mapping`, `Iterable`, `Sequence` from `collections.abc`, not `typing`
- All public methods must have type hints
- No dead code or commented-out blocks

## Commit messages

We use [Conventional Commits](https://www.conventionalcommits.org/). CI validates this automatically.

```
feat: add swipe-to-refresh action
fix: handle None timeout in Waiter.until
chore: update ruff to 0.10.0
docs: add troubleshooting entry for WEBVIEW detection
test: add coverage for ApiClient.patch
refactor: simplify device resolution fallback logic
```

## Pull request guidelines

1. One logical change per PR
2. Include tests proving new behavior **and** unchanged existing behavior
3. Update docs if you add/change a fixture, hook, CLI flag, or public method
4. All CI checks must be green (lint, type check, tests, coverage gate)
5. Keep the PR description concise: what changed and why

## Project layout

```
src/appium_pytest_kit/          # package source
  _internal/                    # non-public modules (no deprecation required to change)
tests/unit/                     # unit tests (testpaths for pytest)
examples/                       # example projects
docs/                           # documentation
scripts/                        # CI/release automation
```

## Adding a new feature

1. Implement in the appropriate module under `src/appium_pytest_kit/`
2. Export from `__init__.py` if it's public API
3. Add unit tests in `tests/unit/test_<module>.py`
4. Update `docs/` and `README.md`
5. If it's an architecture-impacting change, add an ADR in `docs/decisions/`

## Reporting bugs

Open an issue at [GitHub Issues](https://github.com/gianlucasoare/appium-pytest-kit/issues) with:

- Python and appium-pytest-kit versions
- Minimal reproduction steps
- Expected vs actual behavior
- Relevant logs (with `--log-cli-level=DEBUG` output if possible)

## Questions?

Open a discussion or issue on GitHub. We're happy to help.
