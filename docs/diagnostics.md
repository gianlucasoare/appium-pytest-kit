# Failure Diagnostics and Video

When a test fails, `appium-pytest-kit` automatically captures artifacts to help you understand what went wrong.

---

## What gets captured on failure

On any test that fails in the `call` phase, the framework automatically runs:

1. **Screenshot** → `artifacts/screenshots/<test_id>.png`
2. **Page source** → `artifacts/pagesource/<test_id>.xml`
3. **Device logs** → `artifacts/device_logs/<test_id>.log` (`adb logcat` / iOS logs)
4. **Session log** → `artifacts/session_logs/<test_id>.log` (from Appium `driver.get_log(...)`)
5. **Video** (if policy allows) → `artifacts/videos/<test_id>.mp4`

This happens without any configuration — the default `artifacts_dir` is `artifacts/`.

---

## Configure the artifacts directory

```env
APP_ARTIFACTS_DIR=test-artifacts      # custom root directory
```

```bash
pytest --app-artifacts-dir /tmp/test-artifacts
```

The framework creates subdirectories automatically:
```
artifacts/
├── screenshots/
│   └── tests__test_login__test_wrong_password.png
├── pagesource/
│   └── tests__test_login__test_wrong_password.xml
├── device_logs/
│   └── tests__test_login__test_wrong_password.log
├── session_logs/
│   └── tests__test_login__test_wrong_password.log
└── videos/
    └── tests__test_login__test_wrong_password.mp4
```

Device log capture is best-effort and depends on platform tools:
- Android: `adb logcat -d`
- iOS Simulator: `xcrun simctl spawn <udid|booted> log show --last 15m`
- iOS real device: tries `xcrun devicectl ...` / `idevicesyslog` when available

### Artifact redaction

You can redact sensitive values from text artifacts (page source, device logs,
session logs):

```env
APP_ARTIFACT_REDACTION_ENABLED=true
APP_ARTIFACT_REDACTION_REPLACEMENT=[MASKED]
APP_ARTIFACT_REDACTION_PATTERNS=email=([^\s]+),session=([A-Za-z0-9]+)
```

Optional strict screenshot privacy mode:

```env
APP_ARTIFACT_REDACT_SCREENSHOTS=true
```

When enabled, screenshots are replaced with a placeholder image instead of raw
pixels from the app UI.

---

## Video recording

Video is captured per test using Appium's built-in screen recording.

### Policy options

```env
APP_VIDEO_POLICY=never    # default — no recording
APP_VIDEO_POLICY=failed   # record every test; save only when test fails
APP_VIDEO_POLICY=always   # record every test; always save
APP_CLEAN_ARTIFACTS_ON_START=true  # optional: wipe old artifacts before the run
```

```bash
pytest --app-video-policy failed
pytest --app-video-policy always
```

### iOS Simulator limitation

iOS Simulator does not support screen recording via Appium. When `APP_IS_SIMULATOR=true`, video capture is silently skipped regardless of policy.

Physical iOS devices and all Android devices/emulators support recording.

---

## Allure integration

When `allure-pytest` is installed, screenshots, page source, and device logs are automatically attached to Allure reports — no configuration required.

### Install Allure support

```bash
pip install "appium-pytest-kit[allure]"
# or directly:
pip install allure-pytest
```

### Run with Allure

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

Allure will show screenshots, page source, and device logs in the test report for every failing test.

If `allure-pytest` is not installed, Allure attachment is silently skipped — no error or warning.

---

## JSON run summary

Enable the built-in JSON report:

```env
APP_REPORTING_ENABLED=true
APP_REPORT_DIR=artifacts/appium-pytest-kit
```

After the session, `artifacts/appium-pytest-kit/summary.json` is written:

```json
{
  "totals": {
    "passed": 8,
    "failed": 1,
    "skipped": 2
  },
  "tests": [
    {
      "nodeid": "tests/test_login.py::test_successful_login",
      "outcome": "passed",
      "duration": 4.23
    },
    {
      "nodeid": "tests/test_login.py::test_wrong_password",
      "outcome": "failed",
      "duration": 3.87
    }
  ]
}
```

When retries are enabled, `artifacts/appium-pytest-kit/flake-summary.json` is
also written with:
- tests that needed retries
- flaky tests that passed after retry
- tests that still failed after all retries
- top failure signatures and locator patterns

Additionally, `artifacts/appium-pytest-kit/flake-trend.json` keeps a rolling
history of recent runs (default last 30) and computes deltas vs the previous run.

With `pytest-xdist`, each worker writes its own intermediate summary and the
controller merges them into a single final `summary.json`.
The same merge is applied for `flake-summary.json`, and the controller updates
`flake-trend.json` from the merged flake summary.

To enforce flake quality gates in CI, run:

```bash
python scripts/check_flake_thresholds.py \
  --summary artifacts/appium-pytest-kit/flake-summary.json \
  --trend artifacts/appium-pytest-kit/flake-trend.json \
  --max-flaky-tests 0 \
  --max-final-failed-after-retries 0
```

If performance telemetry is enabled (`APP_PERF_ENABLED=true`), the same report
directory also includes:
- `perf-summary.json`
- `perf-trend.json`

See [Performance checks](performance.md) for details.

Only the `call` phase is recorded (setup/teardown failures are tracked by pytest separately).

---

## Artifact capture failures

If the driver is in a bad state when a failure occurs (e.g. session already closed), the framework will emit a `UserWarning` instead of silently skipping:

```
UserWarning: Failed to capture screenshot for 'tests/test_login.py::test_something': ...
```

These warnings appear in the pytest output (`-W` section). They do not fail the test.

---

## Disable artifact capture

To disable all artifact capture (not recommended for CI):

```env
# There is no explicit disable switch.
# Artifacts are only written on test failure.
# Use APP_ARTIFACTS_DIR to control where they go.
APP_ARTIFACTS_DIR=/dev/null   # Unix: discard everything
```

---

## CI integration tips

### GitHub Actions — upload artifacts

```yaml
- name: Run tests
  run: pytest -m integration --app-video-policy failed

- name: Upload test artifacts
  uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: test-artifacts
    path: artifacts/
    retention-days: 7
```

### GitLab CI — artifacts

```yaml
test:
  script:
    - pytest -m integration --app-video-policy failed
  artifacts:
    when: on_failure
    paths:
      - artifacts/
    expire_in: 1 week
```
