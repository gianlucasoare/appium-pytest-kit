# Workflow: Release To PyPI

## Purpose

Publish a verified package release with traceable automation.

## Steps

1. Bump version in `pyproject.toml`.
2. Run release preflight:
   `ruff check .` + `pytest -q` + `pytest -q -n 2 -m "not quarantine"`.
3. Build package artifacts (`python3 -m build`).
4. Validate artifacts (`python3 -m twine check dist/*`).
5. Generate/update changelog and release notes.
6. Tag release as `vX.Y.Z` matching project version.
7. Push tag and monitor release workflow.
8. Verify package on PyPI and GitHub release notes.
9. Run install smoke validation on published version.

## Exit Criteria

- Tag/version consistent.
- PyPI publish successful.
- Release artifacts and notes available.
- Published package installs and imports successfully.
