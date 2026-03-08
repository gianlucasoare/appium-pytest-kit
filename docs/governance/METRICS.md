# Metrics

Metrics used to manage framework health and delivery quality.

## Reliability Metrics

| Metric | Definition | Source | Target |
|---|---|---|---|
| `flake_tests` | Number of tests that pass only after retry | `flake-summary.json` | `0` in main lane |
| `final_failed_after_retries` | Tests still failing after all retries | `flake-summary.json` | `0` |
| `retries_executed_total` | Number of retry attempts used | `flake-summary.json` | non-increasing trend |
| `quarantine_count` | Number of tests marked `quarantine` | pytest collection/report | controlled, time-bounded |

## Performance Metrics

| Metric | Definition | Source | Target |
|---|---|---|---|
| `test_ms_p95` | p95 call duration across measured tests | `perf-summary.json` | team-defined budget |
| `action_ms_p95` | p95 action latency | `perf-summary.json` | team-defined budget |
| `session_start_ms_p95` | p95 driver/session startup latency | `perf-summary.json` | team-defined budget |
| `budget_violations` | Count of soft perf budget breaches | `perf-summary.json` | trending to `0` |

## Delivery Metrics

| Metric | Definition | Source | Target |
|---|---|---|---|
| `ci_pass_rate` | Successful CI runs / total runs | CI dashboard | > 95% |
| `mean_time_to_fix_ci` | Average time from CI fail to merged fix | issue/PR tracking | decreasing |
| `release_success_rate` | Successful release workflows / total release attempts | Actions history | 100% |

## Governance Rules

- Review thresholds monthly or after major architecture changes.
- Use trend deltas to detect regressions early.
- Every metric must have an owner in `OWNERS.md`.
