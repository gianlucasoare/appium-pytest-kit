---
name: appium-kit-release-validator
description: Execute the mandatory release preflight sequence for appium-pytest-kit and decide whether release is ready. Use when validating lint, tests, xdist, build, twine checks, version and tag consistency, changelog state, and release-blocking failures before publishing.
---

# Appium Kit Release Validator

Use this skill when you need a release verdict, not just a loose checklist.

## Required Sequence

1. `python3 -m ruff check .`
2. `python3 -m pytest -q`
3. `python3 -m pytest -q -n 2 -m "not quarantine"`
4. `python3 -m build`
5. `python3 -m twine check dist/*`

Do not call the package release-ready if any step fails.

## Additional Checks

- Compare the intended tag with the version in `pyproject.toml`.
- Check that `CHANGELOG.md` covers the target version.
- Verify no `.env` files or secrets are staged for release work.

## Reporting

- Report each step as pass or fail.
- Include failure excerpts for any blocked step.
- Stop the release verdict at the first blocker.
- End with `RELEASE READY` or `RELEASE BLOCKED`.
