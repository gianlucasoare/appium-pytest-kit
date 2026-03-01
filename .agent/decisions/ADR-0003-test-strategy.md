# ADR-0003: Test Strategy Taxonomy

## Status

Accepted

## Context

Mixed-purpose tests made suites hard to maintain and prioritize.

## Decision

Classify tests by intent and stability:
- `smoke`: critical path, fast feedback.
- `regression`: broad behavior coverage.
- `quarantine`: known unstable, isolated lane.

## Consequences

- Cleaner CI routing and clearer ownership.
- Requires regular quarantine cleanup.
