# Playbook: Performance Budget Rollout

## Goal

Move from no performance enforcement to stable CI budgets.

## Phases

1. Telemetry only (`APP_PERF_ENABLED=true`).
2. Soft budgets with warnings.
3. Hard gates in CI (`check_perf_thresholds.py`).

## Baseline Rules

- Collect at least 1-2 weeks of trend data.
- Use p95 metrics for thresholds.
- Revisit budgets after major architecture changes.
