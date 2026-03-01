# Security Baseline

Minimum security controls for this repository.

## Secrets And Credentials

- Never commit `.env` with real secrets.
- Use repository/environment secrets for CI only.
- Rotate compromised tokens immediately.
- Treat PyPI and GitHub release credentials as high-impact assets.

## Artifact Safety

- Prefer `APP_ARTIFACT_REDACTION_ENABLED=true` in CI.
- Use screenshot redaction where data exposure risk is high.
- Upload only required artifacts with retention limits.

## Dependency Hygiene

- Keep dependencies pinned by policy where possible.
- Run dependency checks regularly in CI.
- Patch critical vulnerabilities as priority work.

## Release Security

- Publish only from guarded tagged workflows.
- Enforce tag/version consistency.
- Optionally require signed tags for release.

## Incident Response

- Use outage playbooks in `.agent/playbooks/`.
- Record incident summary and follow-up actions in ADR or issue tracker.
