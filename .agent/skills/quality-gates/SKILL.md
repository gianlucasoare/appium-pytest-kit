---
name: quality-gates
description: Skill for defining and enforcing measurable quality thresholds (flake rate, performance budgets, reliability signals) in CI.
---

# Quality Gates

## Use This Skill When

- Introducing or tuning CI pass/fail criteria.
- Managing flaky test and performance thresholds.
- Converting metrics into enforceable policy.

## Gate Design

1. Start with telemetry-only period.
2. Set baseline from historical data.
3. Enable soft warnings.
4. Enable hard fail for stable thresholds.

## Required Properties

- Clearly defined metric source.
- Deterministic threshold interpretation.
- Actionable failure output.
- Documented owner and review cadence.
