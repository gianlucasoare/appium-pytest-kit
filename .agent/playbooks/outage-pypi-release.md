# Outage Playbook: PyPI Release Failure

## Trigger

- Release workflow fails before or during publish.
- Package not visible/updated on PyPI after successful tag push.

## Immediate Response

1. Identify failing step in release workflow logs.
2. Confirm tag/version match (`vX.Y.Z` vs `pyproject.toml`).
3. Validate build artifacts and `twine check` output.
4. Confirm publish guard and trusted publishing config.

## Containment

- Do not retag until root cause is clear.
- If required, cut a new patch version instead of force-updating tags.
- Communicate release hold to stakeholders.

## Recovery Validation

- Release workflow succeeds end-to-end.
- Package appears on PyPI with expected version.
- GitHub release notes/changelog are aligned.

## Follow-up

- Document cause and add missing guard/checks.
- Update release checklist/template if the gap was procedural.
