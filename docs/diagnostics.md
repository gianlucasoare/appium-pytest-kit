# Failure Diagnostics and Video

When a test fails, `appium-pytest-kit` automatically captures artifacts to help you understand what went wrong.

---

## What gets captured on failure

On any test that fails in the `call` phase, the framework automatically runs:

1. **Screenshot** → `artifacts/screenshots/<test_id>.png`
2. **Page source** → `artifacts/pagesource/<test_id>.xml`
3. **Video** (if policy allows) → `artifacts/videos/<test_id>.mp4`

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
└── videos/
    └── tests__test_login__test_wrong_password.mp4
```

---

## Video recording

Video is captured per test using Appium's built-in screen recording.

### Policy options

```env
APP_VIDEO_POLICY=never    # default — no recording
APP_VIDEO_POLICY=failed   # record every test; save only when test fails
APP_VIDEO_POLICY=always   # record every test; always save
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

When `allure-pytest` is installed, screenshots and page source are automatically attached to Allure reports — no configuration required.

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

Allure will show screenshots and page source inline in the test report for every failing test.

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
