# CLI Reference

All CLI flags for both the `appium-pytest-kit-init` scaffolding tool and the
`pytest` runner options registered by the plugin.

---

## `appium-pytest-kit-init`

Generates configuration files and scaffolds new projects.

```bash
# Generate a .env template in the current directory
appium-pytest-kit-init

# Write the .env to a custom path
appium-pytest-kit-init --path path/to/.env

# Overwrite an existing .env
appium-pytest-kit-init --force

# Scaffold a full project structure (pages/, flows/, tests/, devices.yaml, …)
appium-pytest-kit-init --framework

# Scaffold into a named subdirectory
appium-pytest-kit-init --framework --root my-project

# Overwrite an existing scaffold
appium-pytest-kit-init --framework --root my-project --force
```

| Flag | Default | Description |
|---|---|---|
| `--path PATH` | `.env` | Output path for the env template |
| `--framework` | off | Scaffold a full project structure |
| `--root DIR` | `.` | Root directory for the framework scaffold |
| `--force` | off | Overwrite files that already exist |

---

## `pytest` CLI flags

All flags below are registered by the plugin and take precedence over `.env`
and environment variables.

### Environment file

```bash
# Load settings from a non-default .env file
pytest --app-env-file path/to/.env.staging
pytest --app-env-file envs/ci.env
```

| Flag | Description |
|---|---|
| `--app-env-file PATH` | Path to a custom env file (default: `.env`) |

---

### Platform

```bash
pytest --app-platform android
pytest --app-platform ios
```

| Flag | Values | Description |
|---|---|---|
| `--app-platform VALUE` | `android`, `ios` | Target platform |

---

### Appium server

```bash
# Point to a remote Appium server
pytest --app-appium-url http://192.168.1.50:4723

# Let the kit start and stop Appium automatically
pytest --app-manage-appium-server

# Disable auto-management (back to explicit URL)
pytest --no-app-manage-appium-server

# Probe /status on external Appium before creating sessions (default enabled)
pytest --app-preflight-status
pytest --no-app-preflight-status
```

| Flag | Description |
|---|---|
| `--app-appium-url URL` | Appium server URL (default: `http://127.0.0.1:4723`) |
| `--appium-url URL` | Legacy alias for `--app-appium-url` |
| `--app-manage-appium-server` | Start a local Appium server automatically |
| `--no-app-manage-appium-server` | Do not start a local Appium server |
| `--app-preflight-status` | Validate external Appium `<url>/status` before use |
| `--no-app-preflight-status` | Skip external Appium status preflight |

---

### Device targeting

```bash
# Target a specific device by name
pytest --app-device-name "Pixel 7"
pytest --app-device-name "iPhone 15 Pro"

# Pin the OS version
pytest --app-platform-version 14
pytest --app-platform-version 17.4

# Target by UDID / serial (required when multiple devices are connected)
pytest --app-udid emulator-5554
pytest --app-udid 00008110-001234567890

# Mark target as a simulator (iOS)
pytest --app-is-simulator
pytest --no-app-is-simulator

# Use a named profile from data/devices.yaml
pytest --app-device-profile pixel7
pytest --app-device-profile iphone15_sim

# Use a custom devices.yaml file
pytest --app-devices-yaml path/to/devices.yaml
```

| Flag | Description |
|---|---|
| `--app-device-name NAME` | Human-readable device name |
| `--app-platform-version VER` | OS version string, e.g. `14` or `17.4` |
| `--app-udid ID` | Device serial (Android) or UDID (iOS) |
| `--app-is-simulator` | Mark device as a simulator |
| `--no-app-is-simulator` | Mark device as a real device |
| `--app-device-profile NAME` | Profile key from `devices.yaml` |
| `--app-devices-yaml PATH` | Path to the devices YAML file |

---

### App under test

```bash
# Install and launch an APK or IPA
pytest --app-app /path/to/app.apk
pytest --app-app /path/to/app.ipa

# Launch an already-installed Android app
pytest --app-app-package com.example.myapp
pytest --app-app-activity .MainActivity

# Launch an already-installed iOS app
pytest --app-bundle-id com.example.MyApp

# Auto-discover latest build from app_builds/
pytest --app-auto-discover
pytest --app-builds-dir app_builds
```

| Flag | Platform | Description |
|---|---|---|
| `--app-app PATH` | both | Full path to the `.apk` or `.ipa` to install |
| `--app-app-package PKG` | Android | App package name |
| `--app-app-activity ACTIVITY` | Android | Main activity to launch, e.g. `.MainActivity` |
| `--app-bundle-id ID` | iOS | Bundle identifier |
| `--app-auto-discover` | both | Auto-pick latest build from `app_builds` when `--app-app` is not set |
| `--no-app-auto-discover` | both | Disable build auto-discovery |
| `--app-builds-dir PATH` | both | Root path for auto-discovery (`android/`, `ios/simulator/`, `ios/device/`) |

---

### Session mode

```bash
# Fresh driver per test — maximum isolation (default)
pytest --app-session-mode clean

# One shared driver for the whole suite — faster
pytest --app-session-mode clean-session

# Shared driver, kept alive after failures — for debugging
pytest --app-session-mode debug
```

| Flag | Values | Description |
|---|---|---|
| `--app-session-mode VALUE` | `clean`, `clean-session`, `debug` | Driver lifecycle strategy |

---

### Waits and timeouts

```bash
# Set explicit wait timeout used by Waiter / MobileActions
pytest --app-override APP_EXPLICIT_WAIT_TIMEOUT=20

# Set Appium implicit wait (driver-level, seconds)
pytest --app-implicit-wait 2
```

| Flag | Description |
|---|---|
| `--app-implicit-wait SECS` | Appium driver-level implicit wait in seconds (default: `0`) |
| `--app-override APP_EXPLICIT_WAIT_TIMEOUT=N` | `Waiter` default timeout in seconds (default: `10`) |

---

### Capabilities

```bash
# Pass extra Appium capabilities as a JSON object
pytest --app-capabilities-json '{"autoGrantPermissions": true}'
pytest --app-capabilities-json '{"wdaLocalPort": 8100, "autoAcceptAlerts": true}'
```

| Flag | Description |
|---|---|
| `--app-capabilities-json JSON` | Extra capabilities merged into every session (JSON object string) |

---

### Video recording

```bash
# Record video only when a test fails (saved to artifacts/videos/)
pytest --app-video-policy failed

# Record video for every test
pytest --app-video-policy always

# No recording (default)
pytest --app-video-policy never
```

| Flag | Values | Description |
|---|---|---|
| `--app-video-policy VALUE` | `never`, `failed`, `always` | When to save screen recordings |

---

### Artifacts

```bash
# Change the artifacts output directory
pytest --app-artifacts-dir test-output/artifacts

# Optional: wipe old artifacts before test session starts
pytest --app-clean-artifacts-on-start
pytest --no-app-clean-artifacts-on-start
```

| Flag | Default | Description |
|---|---|---|
| `--app-artifacts-dir PATH` | `artifacts` | Root directory for screenshots, videos, and page sources |
| `--app-clean-artifacts-on-start` | `false` | Remove existing artifact files before the run |
| `--no-app-clean-artifacts-on-start` | `false` | Keep existing artifact files |

---

### Reporting

```bash
# Generate a JSON summary report to artifacts/appium-pytest-kit/summary.json
pytest --app-reporting-enabled

# Disable reporting explicitly
pytest --no-app-reporting-enabled
```

| Flag | Description |
|---|---|
| `--app-reporting-enabled` | Write a JSON test summary at the end of the session |
| `--no-app-reporting-enabled` | Do not write a JSON summary |

---

### Strict configuration

```bash
# Fail fast on unknown --app-override keys and unknown capability keys
pytest --app-strict-config

# Disable strict validation explicitly
pytest --no-app-strict-config
```

| Flag | Description |
|---|---|
| `--app-strict-config` | Enable strict configuration validation |
| `--no-app-strict-config` | Disable strict configuration validation |

---

### Logging

`appium-pytest-kit` emits structured log messages through Python's standard
`logging` module — no extra dependencies.  Use pytest's built-in log flags to
surface them.

```bash
# Print INFO logs live (session lifecycle, artifacts, device resolution)
pytest --log-cli-level=INFO

# Print DEBUG logs live (every wait, tap, type, assertion, scroll)
pytest --log-cli-level=DEBUG

# Capture logs silently; only shown on test failure
pytest --log-level=DEBUG

# Write captured logs to a file
pytest --log-cli-level=INFO --log-file=pytest.log --log-file-level=DEBUG
```

| Flag | Description |
|---|---|
| `--log-cli-level LEVEL` | Stream logs to the terminal at this level during the run |
| `--log-level LEVEL` | Capture logs at this level; shown in failure output |
| `--log-file PATH` | Write captured logs to a file |
| `--log-file-level LEVEL` | Log level for the file output (default: same as `--log-level`) |

Valid levels (standard Python): `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

#### Logger hierarchy

All appium-pytest-kit loggers are children of `appium_pytest_kit`, so you can
filter them precisely or silence them entirely:

```ini
# pyproject.toml — enable for CI without touching other loggers
[tool.pytest.ini_options]
log_cli       = true
log_cli_level = "INFO"
log_level     = "DEBUG"   # also available in failure output
```

```python
# conftest.py — silence kit logs for a noisy test
import logging
logging.getLogger("appium_pytest_kit").setLevel(logging.WARNING)
```

#### What each level shows

| Level | Source module | Sample message |
|---|---|---|
| `INFO` | `pytest_plugin` | `driver:created  session=4f2a1b  platform=android  node=tests/...` |
| `INFO` | `pytest_plugin` | `driver:reuse  session=4f2a1b  node=...` |
| `INFO` | `pytest_plugin` | `retry:keep-alive  attempt=1/2  node=...` |
| `INFO` | `pytest_plugin` | `driver:quit  session=4f2a1b  node=...` |
| `INFO` | `pytest_plugin` | `artifact:screenshot  artifacts/screenshots/test_foo.png` |
| `INFO` | `pytest_plugin` | `artifact:device_logs  artifacts/device_logs/test_foo.log` |
| `INFO` | `pytest_plugin` | `artifact:video  artifacts/videos/test_foo.mp4` |
| `INFO` | `_internal.device_resolver` | `device:tier-1 (explicit)  name='Pixel 7'  udid=emulator-5554` |
| `INFO` | `_internal.server` | `server:starting  host=127.0.0.1  port=4723  timeout=30000ms` |
| `INFO` | `_internal.video` | `video:started` |
| `DEBUG` | `waits` | `wait:visibility  ('id', 'username')  timeout=10.0s` |
| `DEBUG` | `waits` | `wait:clickable  ('accessibility id', 'btn')  timeout=10.0s` |
| `DEBUG` | `waits` | `wait:invisibility  ('id', 'spinner')  timeout=5.0s` |
| `DEBUG` | `actions` | `tap  ('accessibility id', 'submit_button')` |
| `DEBUG` | `actions` | `type_text  ('id', 'username')  value='testuser'  clear_first=True` |
| `DEBUG` | `actions` | `assert:text  ('id', 'result')  expected='42'` |
| `DEBUG` | `actions` | `swipe  (400,700)->(400,200)  duration=800ms` |

---

### Arbitrary overrides

`--app-override` lets you set any `APP_*` setting that does not have a
dedicated flag. It is repeatable.

```bash
# Single override
pytest --app-override APP_EXPLICIT_WAIT_TIMEOUT=15

# Multiple overrides
pytest \
  --app-override APP_EXPLICIT_WAIT_TIMEOUT=15 \
  --app-override APP_NEW_COMMAND_TIMEOUT=60 \
  --app-override APP_NO_RESET=true
```

Format: `KEY=VALUE` where KEY can be:
- a full `APP_*` setting name (for example `APP_EXPLICIT_WAIT_TIMEOUT`)
- a setting field name (for example `noReset`)
- a capability key (for example `autoGrantPermissions`)

When strict mode is enabled (`--app-strict-config`), unknown capability keys are rejected,
and unknown `APP_*` environment setting keys also fail fast.

---

## Retry (pytest-retry)

Install the optional extra to enable retry support:

```bash
pip install "appium-pytest-kit[retry]"
# or everything at once
pip install "appium-pytest-kit[all]"
```

### How retries work with appium-pytest-kit

When a test is retried, **the same Appium session is reused** — the driver is
not quit and recreated between attempts.  This means:

- No session startup overhead on each retry
- The app is still running in the state it was left in after the failure
- Once a test passes or all retries are exhausted, the session is quit and
  the next test starts with a fresh session — identical to how
  `appium-framework-setup` behaves with `pytest-rerunfailures`

### CLI flags

```bash
# Retry every failed test up to 2 extra times (3 total attempts)
pytest --retries 2

# Wait 1 second between retry attempts
pytest --retries 2 --retry-delay 1

# Only retry on specific exception types
pytest --retries 2 --retry-outcome failed

# Combine with other flags
pytest --retries 2 --retry-delay 1 --app-session-mode clean -m smoke
```

| Flag | Default | Description |
|---|---|---|
| `--retries N` | `0` | Retry each failed test up to N additional times |
| `--retry-delay SECS` | `0` | Seconds to wait between retry attempts |
| `--retry-outcome OUTCOME` | `failed` | Outcome to retry on (`failed`, `error`, or `all`) |

---

## Parallel (pytest-xdist)

Install the optional extra:

```bash
pip install "appium-pytest-kit[xdist]"
# or everything at once
pip install "appium-pytest-kit[all]"
```

Run tests with workers:

```bash
pytest -n 4
```

Worker isolation applied automatically:
- Android: default `systemPort = 8200 + worker_index` when not explicitly provided.
- iOS: default `wdaLocalPort = 8100 + worker_index` and
  `webkitDebugProxyPort = 27753 + worker_index` when not explicitly provided.
- Managed server mode: each worker starts Appium on
  `APP_APPIUM_PORT + worker_index`.

### Per-test marker

Use `@pytest.mark.flaky` to configure retries for a single test or class,
overriding the global `--retries` value.

```python
import pytest

# Retry this test up to 2 extra times (3 total attempts)
@pytest.mark.flaky(retries=2)
def test_flaky_animation(driver, actions):
    actions.tap((AppiumBy.ID, "start_btn"))
    actions.assert_displayed((AppiumBy.ID, "result_screen"))


# Retry with a 2-second delay between attempts
@pytest.mark.flaky(retries=2, delay=2)
def test_network_dependent(driver, actions):
    actions.tap((AppiumBy.ID, "sync_btn"))
    actions.assert_displayed((AppiumBy.ID, "synced_icon"))


# Apply to an entire class (bare marker → 1 retry by default)
@pytest.mark.flaky
class TestCheckoutFlow:

    def test_add_to_cart(self, actions):
        ...

    def test_proceed_to_payment(self, actions):
        ...
```

| Argument | Default | Description |
|---|---|---|
| `retries` | `1` | Number of *extra* retry attempts (e.g. `retries=2` → 3 total runs) |
| `delay` | `0` | Seconds to wait before the next attempt |

### Fail-fast on retry exhaustion

By default pytest continues running the rest of the suite even after a test
exhausts all its retries.  Use `--app-fail-fast` to stop immediately once a
test is definitively failed (all attempts used up).

```bash
# Stop the suite the moment any test fails after all its retries
pytest --retries 2 --app-fail-fast

# Per-test retry + fail-fast
pytest --app-fail-fast
# (tests use @pytest.mark.flaky(retries=3) individually)
```

**`--app-fail-fast` vs pytest's `-x`**

| Flag | Stops on | Retries happen first | Use case |
|---|---|---|---|
| *(default — no flag)* | Never | Yes | Run entire suite, collect all results |
| `-x` | First failure of any attempt | No | Hard stop on any error |
| `--app-fail-fast` | Final failure after all retries | Yes | Let flaky tests retry, stop on real failures |

The default behaviour (no flag) always runs the full suite regardless of failures.
Use `--app-fail-fast` when you want retries to finish but don't want to waste
time running the rest of the suite once something is definitively broken.

### Common retry patterns

```bash
# Retry all smoke tests on CI — catches transient timing failures
pytest -m smoke --retries 2 --retry-delay 1

# Retry a specific failing test while debugging
pytest tests/test_login.py::TestLoginSuccess::test_valid_credentials_open_home --retries 3

# Stop on real failures, let timing flakiness retry
pytest --retries 2 --app-fail-fast
```

---

## Common command examples

### Run smoke tests on Android emulator (auto-detect)

```bash
pytest -m smoke --app-platform android
```

### Run on a specific physical Android device

```bash
pytest --app-udid R9JT204XXXX --app-platform android
```

### Run iOS tests on a simulator profile

```bash
pytest --app-platform ios --app-device-profile iphone15_sim
```

### Point to a staging Appium server

```bash
pytest --app-appium-url http://10.0.1.100:4723 --app-platform android
```

### Faster suite with a shared driver session

```bash
pytest --app-session-mode clean-session
```

### Debug a failing test (keep driver alive on failure)

```bash
pytest --app-session-mode debug -k test_login_success
```

### Record video for failures only

```bash
pytest --app-video-policy failed
```

### Increase wait timeout for a slow CI device

```bash
pytest --app-override APP_EXPLICIT_WAIT_TIMEOUT=30
```

### Run with a non-default .env (e.g. staging environment)

```bash
pytest --app-env-file .env.staging
```

### Override app package without editing .env

```bash
pytest \
  --app-platform android \
  --app-app-package com.example.staging \
  --app-app-activity .MainActivity
```

### Full CI invocation example

```bash
pytest \
  --app-platform android \
  --app-udid emulator-5554 \
  --app-app-package com.example.myapp \
  --app-app-activity .MainActivity \
  --app-session-mode clean-session \
  --app-video-policy failed \
  --app-reporting-enabled \
  -m smoke \
  -v
```

### Full CI invocation with retry + fail-fast (requires `[retry]` extra)

```bash
pytest \
  --app-platform android \
  --app-udid emulator-5554 \
  --app-app-package com.example.myapp \
  --app-app-activity .MainActivity \
  --retries 2 \
  --retry-delay 1 \
  --app-fail-fast \
  --app-video-policy failed \
  --app-reporting-enabled \
  -m smoke \
  -v
```

### Full iOS simulator invocation example

```bash
pytest \
  --app-platform ios \
  --app-device-name "iPhone 15 Pro" \
  --app-platform-version 17.4 \
  --app-is-simulator \
  --app-bundle-id com.example.MyApp \
  --app-capabilities-json '{"autoAcceptAlerts": true}' \
  --app-session-mode clean \
  -m regression \
  -v
```

### Debug a flaky test with full logs

```bash
# See every wait and action while the test runs
pytest tests/test_checkout.py::test_place_order \
  --log-cli-level=DEBUG \
  --app-session-mode debug \
  -s
```

### CI run with session lifecycle logs

```bash
pytest \
  --app-platform android \
  --app-udid emulator-5554 \
  --app-app-package com.example.myapp \
  --app-app-activity .MainActivity \
  --log-cli-level=INFO \
  --log-file=pytest.log \
  --log-file-level=DEBUG \
  --app-video-policy failed \
  -m smoke \
  -v
```
