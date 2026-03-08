---
name: feature-delivery
description: Ship new framework features safely from requirements through incremental implementation to release readiness.
---

# Feature Delivery

## Use This Skill When

- Implementing new framework features
- Adding fixtures, helpers, or CLI options
- Expanding configuration options
- Shipping any user-facing behavior change

## Procedure

1. Clarify user problem and success criteria
2. Draft implementation boundaries and impacted modules
3. Add or adjust unit tests first where possible
4. Implement incrementally with frequent validation
5. Update docs and CLI/config references
6. Run full test suite and lint
7. Prepare release notes or changelog entry

## Rules

- Tests must prove new and unchanged behavior
- If scaffold output changes, update project-structure and CLI docs in same change set
- Architecture-impacting changes require ADR in `docs/decisions/`
- Backward compatibility preserved unless major version bump

## Definition of Done

- Tests pass locally and in CI
- Docs reflect final behavior
- No unresolved breaking changes
- Changelog entry prepared
