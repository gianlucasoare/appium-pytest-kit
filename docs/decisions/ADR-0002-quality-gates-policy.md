# ADR-0002: Quality Gates Policy

## Status

Accepted

## Context

Flaky failures and performance drift can silently reduce trust in CI.

## Decision

Use telemetry-backed quality gates for flake/performance metrics.
Start soft, then enforce hard thresholds once baselines stabilize.

## Consequences

- Higher confidence in CI signal.
- Requires periodic threshold review.
