# Workflow Rules

This file applies to `.github/workflows/**`.

- Publish only from trusted tag refs, never from branch pushes.
- Keep release tags in `vX.Y.Z` format and in sync with the version in `pyproject.toml`.
- Respect the mandatory release preflight before any publish job or release promotion.
- Prefer `APP_ARTIFACT_REDACTION_ENABLED=true` for artifact safety when workflows produce diagnostics.
- Upload only required artifacts and set retention conservatively.
- Use repository or environment secrets, never committed `.env` files or inline credentials.
- Treat PyPI and GitHub release credentials as high-impact assets.
- After release automation changes, preserve the verification flow for PyPI version, GitHub release notes, and install smoke testing.
