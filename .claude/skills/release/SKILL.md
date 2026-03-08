---
name: release
description: End-to-end PyPI release from version bump through build, publish, and verification.
---

# Release

## Use This Skill When

- Preparing a package release
- Running release preflight checks
- Hardening quality gates for merge or publish
- Updating GitHub workflows for release

## Release Procedure

1. Bump version in `pyproject.toml`
2. Run release preflight (all must pass):
   - `python3 -m ruff check .`
   - `python3 -m pytest -q`
   - `python3 -m pytest -q -n 2 -m "not quarantine"`
   - `python3 -m build`
   - `python3 -m twine check dist/*`
3. Generate/update changelog: `python3 scripts/update_changelog.py --version X.Y.Z`
4. Tag release: `git tag vX.Y.Z` (must match pyproject.toml version)
5. Push tag: `git push origin vX.Y.Z`
6. Monitor release workflow in GitHub Actions
7. Verify package on PyPI and GitHub release notes
8. Run install smoke: `pip install appium-pytest-kit==X.Y.Z` and import check

## CI Requirements

- Main lane for core tests
- Optional lanes for extras and parallel paths
- Dedicated non-blocking quarantine lane
- Explicit quality gates (flake, perf, security as needed)

## Rules

- If any preflight step fails, release is blocked
- Publish only from guarded tagged workflows
- Enforce tag/version consistency
- Never retag until root cause of failure is clear; cut a new patch instead
- Generate release notes automatically

## Definition of Done

- Tag/version consistent
- PyPI publish successful
- Release artifacts and notes available
- Published package installs and imports successfully
