---
name: perf-analysis
description: Analyze performance telemetry data, set and tune budgets, and diagnose action or session latency regressions.
---

# Perf Analysis

## Use This Skill When

- CI performance gate is failing or warning
- Investigating slow test runs or high action latency
- Setting initial performance budgets for a new project
- Reviewing performance trends across releases
- Deciding whether a perf regression is real or noise

## Analysis Procedure

1. **Load the data**: read `artifacts/appium-pytest-kit/perf-summary.json` and `perf-trend.json`
2. **Identify the metric that failed**: action_p95_ms, test_p95_ms, or session_start_p95_ms
3. **Compare against budget**: read `scripts/check_perf_thresholds.py` for current budget values
4. **Check trend**: is this a sudden spike or gradual drift?
5. **Identify the slow operations**: look for individual action measurements in the summary
6. **Correlate with changes**: what changed in the commit range that could affect latency?
7. **Recommend action**: tune budget, optimize code, or quarantine slow test

## Key Metrics

| Metric | Description | Typical Budget |
|--------|-------------|---------------|
| `action_p95_ms` | 95th percentile action duration | ≤ 5000ms |
| `test_p95_ms` | 95th percentile test duration | depends on suite |
| `session_start_p95_ms` | 95th percentile driver creation time | ≤ 30000ms |
| `flaky_tests` | Tests that passed on retry | 0 ideally, ≤ 5% threshold |
| `tests_with_retries` | Tests that required any retry | ≤ 10% threshold |

## Telemetry Configuration

Performance telemetry is controlled by `APP_*` settings:

```bash
APP_PERF_ENABLED=true                    # enable collection
APP_PERF_BUDGET_ACTION_P95_MS=5000       # action latency budget
APP_PERF_BUDGET_SESSION_START_P95_MS=30000  # session start budget
```

## Budget Tuning Process

1. **Establish baseline**: run suite 5+ times and record p95 values
2. **Set initial budget at 2x observed p95**: provides buffer for CI variance
3. **After 2 sprints**: tighten to 1.5x observed p95 if variance is low
4. **Target**: budget at 1.2x observed p95 once the suite is stable

## Investigating Regressions

1. Check if regression appears in specific test(s) or all tests
2. If specific test: inspect waits — look for `for_presence`, `for_clickable` with long timeouts
3. If all tests: check session start time (Appium server, device connection, app launch)
4. If gradual drift: check for uncleaned state (growing artifact dirs, process leaks)
5. If CI-only: check device/emulator cold start vs warm cache differences

## Quality Gate Scripts

```bash
# Validate perf thresholds
python3 scripts/check_perf_thresholds.py \
  --summary artifacts/appium-pytest-kit/perf-summary.json \
  --trend artifacts/appium-pytest-kit/perf-trend.json

# Validate flake thresholds
python3 scripts/check_flake_thresholds.py \
  --summary artifacts/appium-pytest-kit/flake-summary.json \
  --trend artifacts/appium-pytest-kit/flake-trend.json
```

## Rules

- Never tighten budgets based on a single run — use 5+ run averages
- A p95 spike in a single CI run is not a regression — look for trend over 3+ runs
- Session start latency is dominated by device/emulator cold start, not framework code
- Action latency > 2s usually indicates a wait strategy issue, not a performance bug
- Do not optimize for micro-benchmarks; optimize for user-observable test duration

## Definition of Done

- Regression identified as real vs noise
- Root cause traced to specific metric, test, or code path
- Budget adjusted or code fixed based on findings
- Trend data updated and gate passes
