# Errors

All framework-specific exceptions inherit from `AppiumPytestKitError`. This lets you catch any framework error with a single `except` clause, or target specific error types for fine-grained handling.

---

## Exception hierarchy

```
Exception
└── AppiumPytestKitError          base for all framework errors
    ├── ConfigurationError        invalid settings or managed server failure
    ├── DeviceResolutionError     device cannot be resolved
    ├── LaunchValidationError     missing required app launch settings
    ├── WaitTimeoutError          explicit wait condition never passed
    ├── ActionError               tap / type / scroll raised WebDriverException
    ├── DriverCreationError       Appium session could not be created
    ├── ApiRequestError           HTTP request failed or unexpected status
    └── VisualRegressionError     screenshot does not match baseline
```

---

## `AppiumPytestKitError`

The base class. Catch this to handle any framework error:

```python
from appium_pytest_kit import AppiumPytestKitError

try:
    actions.tap(locator)
except AppiumPytestKitError as exc:
    print(f"Framework error: {exc}")
```

---

## `ConfigurationError`

Raised when settings are invalid or the managed Appium server fails to start.

**Common causes:**
- `APP_PLATFORM` set to something other than `android` or `ios`
- `APP_DEVICE_PROFILE` references a profile not found in `devices.yaml`
- `APP_MANAGE_APPIUM_SERVER=true` but `appium` is not on PATH
- `devices.yaml` file not found at the configured path

```python
from appium_pytest_kit import ConfigurationError

try:
    settings = load_settings(env_file="missing.env")
except ConfigurationError as exc:
    print(f"Configuration problem: {exc}")
```

---

## `DeviceResolutionError`

Raised when device resolution fails in a way that is unrecoverable. Distinct from returning `None` (which means no device was found but is non-fatal).

---

## `LaunchValidationError`

Raised when the minimum required app launch capabilities are missing.

- **Android**: needs `APP_APP` or both `APP_APP_PACKAGE` + `APP_APP_ACTIVITY`
- **iOS**: needs `APP_APP` or `APP_BUNDLE_ID`

This is checked before any Appium connection is attempted, so you get a clear error message rather than a cryptic Appium session error.

```
appium_pytest_kit.errors.LaunchValidationError: Android launch requires APP_APP (apk path)
or both APP_APP_PACKAGE + APP_APP_ACTIVITY
```

**Fix:** Add the missing settings to `.env`:

```env
# Android
APP_APP_PACKAGE=com.example.myapp
APP_APP_ACTIVITY=.MainActivity

# iOS
APP_BUNDLE_ID=com.example.MyApp
```

---

## `WaitTimeoutError`

Raised when an explicit wait condition does not pass within the timeout.

Carries structured context:

| Attribute | Type | Description |
|---|---|---|
| `.locator` | `tuple[str, str] \| None` | The locator that was waited on |
| `.timeout` | `float \| None` | The timeout in seconds |

```python
from appium_pytest_kit import WaitTimeoutError

try:
    waiter.for_visibility(("id", "submit_btn"), timeout=5.0)
except WaitTimeoutError as exc:
    print(exc.locator)   # ("id", "submit_btn")
    print(exc.timeout)   # 5.0
    print(str(exc))      # includes locator and timeout context
```

**In tests — skip vs fail:**

```python
try:
    waiter.for_visibility(WELCOME_SCREEN, timeout=15.0)
except WaitTimeoutError:
    pytest.fail("Welcome screen never appeared — login may have failed")

# Or skip if the element is optional
try:
    waiter.for_visibility(OPTIONAL_BANNER, timeout=3.0)
except WaitTimeoutError:
    pytest.skip("Optional banner not shown — skipping banner test")
```

---

## `ActionError`

Raised when a high-level action fails with a `WebDriverException`.

Carries structured context:

| Attribute | Type | Description |
|---|---|---|
| `.locator` | `tuple[str, str] \| None` | The locator the action targeted |
| `.action` | `str \| None` | The action name (e.g. `"tap"`, `"type_text"`) |

```python
from appium_pytest_kit import ActionError

try:
    actions.tap(("id", "missing_btn"))
except ActionError as exc:
    print(exc.action)   # "tap"
    print(exc.locator)  # ("id", "missing_btn")
    print(str(exc))     # "[tap] Tap failed for locator: ('id', 'missing_btn') [id='missing_btn']"
```

---

## `DriverCreationError`

Raised when an Appium session cannot be created. Wraps the underlying connection error.

**Common causes:**
- Appium server is not running at `APP_APPIUM_URL`
- Device is not connected or emulator is not running
- Capabilities are invalid (wrong package name, wrong bundle ID)

```
appium_pytest_kit.errors.DriverCreationError: Failed to create Appium session at http://127.0.0.1:4723
```

**Diagnosis:**
```bash
# Is Appium running?
curl http://127.0.0.1:4723/status

# Is the device connected?
adb devices          # Android
xcrun simctl list    # iOS
```

---

## `ApiRequestError`

Raised when an HTTP request fails or returns an unexpected status code.

Carries structured context:

| Attribute | Type | Description |
|---|---|---|
| `.method` | `str \| None` | HTTP method (GET, POST, etc.) |
| `.url` | `str \| None` | Request URL |
| `.status_code` | `int \| None` | Response status code |

```python
from appium_pytest_kit import ApiRequestError

try:
    api.get("/health", expected_status=200)
except ApiRequestError as exc:
    print(exc.method)       # "GET"
    print(exc.url)          # "http://127.0.0.1:8000/health"
    print(exc.status_code)  # 503
```

---

## `VisualRegressionError`

Raised when a screenshot does not match its baseline beyond the allowed threshold.

Carries structured context:

| Attribute | Type | Description |
|---|---|---|
| `.baseline_path` | `str \| None` | Path to the baseline image |
| `.actual_path` | `str \| None` | Path to the actual screenshot |
| `.diff_ratio` | `float \| None` | Ratio of differing pixels (0.0-1.0) |
| `.threshold` | `float \| None` | Maximum allowed diff ratio |

```python
from appium_pytest_kit import VisualRegressionError

try:
    assert_screenshot_match(driver, test_id, baselines_dir, artifacts_dir)
except VisualRegressionError as exc:
    print(exc.diff_ratio)      # 0.0342
    print(exc.threshold)       # 0.01
    print(exc.baseline_path)   # baselines/android/test_home.png
    print(exc.actual_path)     # artifacts/screenshots/visual/test_home.png
```

Requires the `visual` extra: `pip install appium-pytest-kit[visual]`

---

## Importing errors

All errors are available from the top-level package:

```python
from appium_pytest_kit import (
    AppiumPytestKitError,
    ConfigurationError,
    DeviceResolutionError,
    LaunchValidationError,
    WaitTimeoutError,
    ActionError,
    DriverCreationError,
    ApiRequestError,
    VisualRegressionError,
)
```
