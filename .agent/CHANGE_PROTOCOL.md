# Change Protocol

Policy for safe and predictable framework changes.

## Change Types

- Patch: bug fixes, no API/behavior break.
- Minor: backward-compatible features.
- Major: breaking behavior or API change.

## Required Process

1. Define expected user impact.
2. Add tests proving new and unchanged behavior.
3. Update docs and CLI/config references.
4. If architecture-impacting, add/update ADR.
5. Validate all quality gates before merge.

## Breaking Change Rules

- Must include migration notes in docs/README.
- Must be called out in changelog and release notes.
- Prefer deprecation window before removal when feasible.

## Deprecation Policy

- Mark deprecated behavior in docs immediately.
- Keep compatibility for at least one minor release when practical.
- Remove only after migration path is documented.
