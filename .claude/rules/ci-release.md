---
description: Rules for CI workflows and release scripts
globs:
  - ".github/workflows/**"
  - "scripts/**"
---

# CI and Release Rules

- Release preflight is mandatory before any publish: ruff → pytest → xdist lane → build → twine check
- Git tag must match `pyproject.toml` version exactly (`vX.Y.Z` format)
- Publish only from trusted tag refs, never from branch pushes
- Prefer `APP_ARTIFACT_REDACTION_ENABLED=true` in CI for artifact safety
- Upload only required artifacts with retention limits
- After release: verify PyPI package, GitHub release notes, install smoke test
- CI failure response: start from first traceback, reproduce locally, add regression test
- xdist reporting: safe existence checks for worker artifacts, idempotent merge logic
- Changelog automation: `python3 scripts/update_changelog.py --version X.Y.Z`
- Never commit `.env` with real secrets; use repository/environment secrets only
- Treat PyPI and GitHub release credentials as high-impact assets
