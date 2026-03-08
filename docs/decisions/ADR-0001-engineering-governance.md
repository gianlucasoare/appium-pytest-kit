# ADR-0001: Engineering Governance For Automation Kit

## Status

Accepted

## Context

Rapid feature growth increased risk of inconsistent quality and undocumented tradeoffs.

## Decision

Adopt a standard operating model with reusable skills, explicit workflows,
and ADR-based architecture decisions.

Initially implemented in a custom `.agent/` directory. Migrated to native Claude Code
architecture under `.claude/` (skills, agents, rules) and `CLAUDE.md` for auto-discovery
and auto-loading. Passive documentation (ADRs, templates, governance, playbooks) moved
to `docs/` subdirectories.

## Consequences

- Better consistency and onboarding speed.
- Slight overhead to keep docs and decisions current.
