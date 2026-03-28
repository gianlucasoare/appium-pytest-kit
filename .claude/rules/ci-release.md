---
description: Rules for CI workflows and release scripts
globs:
  - ".github/workflows/**"
  - "scripts/**"
---

# CI and Release Rules

## Release Preflight (all must pass)
- Release preflight is mandatory before any publish: ruff → mypy → pytest → xdist lane → build → twine check
- Git tag must match `pyproject.toml` version exactly (`vX.Y.Z` format)
- Publish only from trusted tag refs, never from branch pushes

## CI Quality Gates
- Lint: `ruff check .` — zero violations
- Type check: `mypy src/appium_pytest_kit/` — zero errors
- Unit tests: `pytest -q -m "not quarantine" --cov --cov-report=term-missing` — coverage gate at 60%
- xdist sanity: `pytest -q -n 2 -m "not quarantine"` — all tests pass under parallel execution
- Flake gate: `scripts/check_flake_thresholds.py` — zero tolerance for flaky tests in CI
- Optional extras: each extra (`yaml`, `allure`, `retry`, `visual`, `all`) tested for import health

## Artifacts & Reporting
- Prefer `APP_ARTIFACT_REDACTION_ENABLED=true` in CI for artifact safety
- Upload only required artifacts with retention limits
- xdist reporting: safe existence checks for worker artifacts, idempotent merge logic

## Post-Release Verification
- After release: verify PyPI package, GitHub release notes, install smoke test
- Verify `pip install appium-pytest-kit==X.Y.Z && python -c "import appium_pytest_kit"` works

## Failure Response
- CI failure response: start from first traceback, reproduce locally, add regression test
- Changelog automation: `python3 scripts/update_changelog.py --version X.Y.Z`

## Secrets & Credentials
- Never commit `.env` with real secrets; use repository/environment secrets only
- Treat PyPI and GitHub release credentials as high-impact assets
- Cloud provider credentials (`BROWSERSTACK_*`, `SAUCE_*`, `AWS_*`) must be CI secrets, never in source
- Never store tokens in workflow files, docs, or issue comments
