---
name: quality-gates
description: Define and enforce measurable quality thresholds for flake rate, performance, and reliability in CI.
---

# Quality Gates

## Use This Skill When

- Introducing or tuning CI pass/fail criteria
- Managing flaky test and performance thresholds
- Converting metrics into enforceable policy
- Reviewing quality gate health

## Gate Design Process

1. Start with telemetry-only period (`APP_PERF_ENABLED=true`)
2. Set baseline from historical data (1-2 weeks minimum)
3. Enable soft warnings
4. Enable hard fail for stable thresholds

## Required Properties

Every gate must have:
- Clearly defined metric source
- Deterministic threshold interpretation
- Actionable failure output
- Documented owner and review cadence

## Key Scripts

- Flake thresholds: `python3 scripts/check_flake_thresholds.py --summary <path> --trend <path>`
- Perf thresholds: `python3 scripts/check_perf_thresholds.py --summary <path> --trend <path>`

## Metrics

| Metric | Source | Target |
|---|---|---|
| `flake_tests` | `flake-summary.json` | `0` in main lane |
| `test_ms_p95` | `perf-summary.json` | team-defined budget |
| `budget_violations` | `perf-summary.json` | trending to `0` |

## Rules

- Review thresholds monthly or after major architecture changes
- Use trend deltas to detect regressions early
- Use p95 metrics for thresholds, not averages
