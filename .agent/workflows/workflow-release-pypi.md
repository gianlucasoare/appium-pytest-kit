# Workflow: Release To PyPI

## Purpose

Publish a verified package release with traceable automation.

## Steps

1. Bump version in `pyproject.toml`.
2. Run full lint/test suite.
3. Generate/update changelog and release notes.
4. Tag release as `vX.Y.Z` matching project version.
5. Push tag and monitor release workflow.
6. Verify package on PyPI and GitHub release notes.

## Exit Criteria

- Tag/version consistent.
- PyPI publish successful.
- Release artifacts and notes available.
