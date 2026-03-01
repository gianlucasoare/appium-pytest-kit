# Performance Checks

`appium-pytest-kit` includes opt-in performance telemetry and soft budget checks.

---

## What gets measured

When performance mode is enabled:

1. **Session start time** (driver creation latency)
2. **Action latency** for instrumented `actions` methods
3. **Per-test call duration**

Artifacts are written under `APP_REPORT_DIR`:
- `perf-summary.json`
- `perf-trend.json`

With `pytest-xdist`, workers write intermediate files and the controller merges
them into a single final report.

---

## Enable performance mode

```env
APP_PERF_ENABLED=true
APP_REPORTING_ENABLED=true
APP_REPORT_DIR=artifacts/appium-pytest-kit
```

or via CLI:

```bash
pytest --app-perf-enabled --app-reporting-enabled
```

---

## Optional soft budgets (warnings only)

```env
APP_PERF_BUDGET_ACTION_MS=800
APP_PERF_BUDGET_TEST_MS=15000
APP_PERF_BUDGET_SESSION_START_MS=6000
```

When a budget is exceeded, the run logs `perf:budget ...` warnings and stores
details in `perf-summary.json` (`budget_violations` section).  
Budgets are non-blocking by default.

---

## Trend history

```env
APP_PERF_TREND_HISTORY_LIMIT=30
```

`perf-trend.json` stores rolling history and delta vs previous run for:
- `tests_measured`
- `action_events_total`
- `budget_violations`
- `session_start_ms_p95`
- `action_ms_p95`
- `test_ms_p95`

---

## CI gate (optional)

Use the helper script to enforce thresholds:

```bash
python scripts/check_perf_thresholds.py \
  --summary artifacts/appium-pytest-kit/perf-summary.json \
  --trend artifacts/appium-pytest-kit/perf-trend.json \
  --max-test-ms-p95 12000 \
  --max-action-ms-p95 1000 \
  --max-session-start-ms-p95 7000 \
  --max-budget-violations 0
```

If any threshold is exceeded, the script exits with code `1`.
