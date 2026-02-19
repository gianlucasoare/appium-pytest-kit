# appium-pytest-kit — Full Documentation

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Installation](#3-installation)
4. [Project setup](#4-project-setup)
5. [Configuration](#5-configuration)
6. [Built-in fixtures](#6-built-in-fixtures)
7. [Writing your first test](#7-writing-your-first-test)
8. [Step-by-step: testing a real Android app](#8-step-by-step-testing-a-real-android-app)
9. [Step-by-step: testing a real iOS app](#9-step-by-step-testing-a-real-ios-app)
10. [Extension hooks](#10-extension-hooks)
11. [Custom capabilities adapter](#11-custom-capabilities-adapter)
12. [Managed Appium server](#12-managed-appium-server)
13. [Reporting](#13-reporting)
14. [Public API reference](#14-public-api-reference)
15. [Error hierarchy](#15-error-hierarchy)
16. [Project structure](#16-project-structure)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. Overview

`appium-pytest-kit` is a pytest plugin library that provides zero-boilerplate Appium 2.x test infrastructure for Python 3.11+.

Install it once, generate a `.env`, and start writing tests immediately. The framework manages:

- Configuration loading (`.env` → env vars → CLI flags)
- Appium server lifecycle (optional)
- Driver session creation and teardown per test
- Explicit waits and generic UI actions
- Optional JSON run report

It is intentionally **thin and generic**. App-specific logic, page objects, and screen abstractions are always your responsibility. The framework gives you the scaffolding — you bring the tests.

---

## 2. Prerequisites

### System requirements

- Python 3.11 or 3.12
- Node.js 18+ (required by Appium)
- Appium 2.x server
- Android or iOS device / emulator / simulator

### Install Appium 2

```bash
npm install -g appium
```

### Install a platform driver

```bash
# Android
appium driver install uiautomator2

# iOS
appium driver install xcuitest
```

### Verify Appium is working

```bash
appium driver list --installed
appium &          # starts the server on http://127.0.0.1:4723
```

---

## 3. Installation

### From PyPI (once published)

```bash
pip install appium-pytest-kit
```

### From GitHub (latest main branch)

```bash
pip install git+https://github.com/gianlucasoare/appium-pytest-kit.git
```

### From GitHub (specific branch or tag)

```bash
# a specific branch
pip install git+https://github.com/gianlucasoare/appium-pytest-kit.git@main

# a specific tag
pip install git+https://github.com/gianlucasoare/appium-pytest-kit.git@v0.1.0
```

### From a local clone (editable, for development)

```bash
git clone https://github.com/gianlucasoare/appium-pytest-kit.git
cd appium-pytest-kit
pip install -e ".[dev]"
```

> The `[dev]` extra installs `ruff` (linter) and `pytest-cov` (coverage).

---

## 4. Project setup

### 4.1 Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install appium-pytest-kit
```

### 4.2 Generate a starter `.env`

```bash
appium-pytest-kit-init
```

This writes a `.env` file in the current directory:

```env
# appium-pytest-kit starter configuration
APP_PLATFORM=android
APP_APPIUM_URL=http://127.0.0.1:4723
APP_MANAGE_APPIUM_SERVER=false
APP_DEVICE_NAME=
APP_PLATFORM_VERSION=
APP_UDID=
APP_APP=
APP_APPIUM_BASE_PATH=/
APP_CAPABILITIES_JSON={}
APP_REPORTING_ENABLED=false
```

To write it to a custom path or overwrite an existing file:

```bash
appium-pytest-kit-init --path config/.env
appium-pytest-kit-init --force        # overwrite if already exists
```

### 4.3 Recommended project layout

```
my-tests/
├── .env                    # device + app configuration (never commit secrets)
├── conftest.py             # project-level fixtures and hook implementations
├── pytest.ini              # or pyproject.toml [tool.pytest.ini_options]
└── tests/
    ├── test_login.py
    ├── test_home.py
    └── ...
```

### 4.4 Minimal `pytest.ini`

```ini
[pytest]
addopts = -ra --strict-markers -m "not integration"
markers =
    integration: requires a running Appium server and a connected device
```

---

## 5. Configuration

### 5.1 Precedence (low → high)

```
defaults in AppiumPytestKitSettings
        ↓
.env file / environment variables
        ↓
pytest CLI flags (--app-*, --app-override)
```

Higher-precedence values always win. This lets you keep safe defaults in `.env` and override specific values per CI run with CLI flags.

### 5.2 All settings

| `.env` key | Python field | Type | Default | Description |
|---|---|---|---|---|
| `APP_PLATFORM` | `platform` | `android\|ios` | `android` | Target platform |
| `APP_APPIUM_URL` | `appium_url` | `str` | `http://127.0.0.1:4723` | Appium server URL |
| `APP_MANAGE_APPIUM_SERVER` | `manage_appium_server` | `bool` | `false` | Start a local Appium process automatically |
| `APP_APPIUM_HOST` | `appium_host` | `str` | `127.0.0.1` | Host for managed server |
| `APP_APPIUM_PORT` | `appium_port` | `int` | `4723` | Port for managed server |
| `APP_APPIUM_BASE_PATH` | `appium_base_path` | `str` | `/` | Base path for managed server |
| `APP_APPIUM_SERVER_ARGS` | `appium_server_args` | `str` (comma-separated) | `""` | Extra CLI args passed to managed Appium |
| `APP_APPIUM_START_TIMEOUT` | `appium_start_timeout` | `float` | `20.0` | Seconds to wait for managed server to start |
| `APP_DEVICE_NAME` | `device_name` | `str\|None` | `None` | Device name capability |
| `APP_PLATFORM_VERSION` | `platform_version` | `str\|None` | `None` | OS version capability |
| `APP_UDID` | `udid` | `str\|None` | `None` | Physical device UDID |
| `APP_APP` | `app` | `str\|None` | `None` | Full path or URL to `.apk` / `.ipa` |
| `APP_APP_PACKAGE` | `app_package` | `str\|None` | `None` | Android app package (e.g. `com.example.app`) |
| `APP_APP_ACTIVITY` | `app_activity` | `str\|None` | `None` | Android launch activity (e.g. `.MainActivity`) |
| `APP_BUNDLE_ID` | `bundle_id` | `str\|None` | `None` | iOS bundle ID (e.g. `com.example.app`) |
| `APP_AUTOMATION_NAME` | `automation_name` | `str\|None` | `None` | Override automation name (defaults: `UiAutomator2` / `XCUITest`) |
| `APP_NEW_COMMAND_TIMEOUT` | `new_command_timeout` | `int` | `120` | Appium session timeout in seconds |
| `APP_NO_RESET` | `no_reset` | `bool` | `false` | Skip app reset between sessions |
| `APP_FULL_RESET` | `full_reset` | `bool` | `false` | Full app reset (uninstall) between sessions |
| `APP_IMPLICIT_WAIT` | `implicit_wait` | `float` | `0.0` | Selenium implicit wait in seconds |
| `APP_CAPABILITIES_JSON` | `capabilities_json` | JSON object | `{}` | Extra capabilities merged last |
| `APP_REPORTING_ENABLED` | `reporting_enabled` | `bool` | `false` | Write JSON summary to `report_dir` |
| `APP_REPORT_DIR` | `report_dir` | `str` | `artifacts/appium-pytest-kit` | Directory for report output |

### 5.3 CLI overrides

Every setting can be overridden at the `pytest` command line:

```bash
pytest --app-platform ios
pytest --appium-url http://192.168.1.10:4723
pytest --app-device-name "Pixel 7"
pytest --app-platform-version "13"
pytest --app-udid emulator-5554
pytest --app-app /path/to/app.apk
pytest --app-app-package com.example.app
pytest --app-app-activity .MainActivity
pytest --app-bundle-id com.example.ios
pytest --app-capabilities-json '{"autoGrantPermissions": true}'
pytest --app-implicit-wait 2.0
pytest --app-manage-appium-server
pytest --no-app-manage-appium-server
pytest --app-reporting-enabled
pytest --no-app-reporting-enabled
```

For any setting not covered by a named flag, use `--app-override`:

```bash
pytest --app-override APP_NEW_COMMAND_TIMEOUT=60
pytest --app-override noReset=true --app-override autoGrantPermissions=true
```

`--app-override` can be repeated and accepts `KEY=VALUE` in any of these forms:
- `APP_FIELD_NAME=value` (env-style, `APP_` prefix stripped automatically)
- `field_name=value` (Python field name)

### 5.4 Using a custom `.env` file path

```bash
pytest --app-env-file /path/to/staging.env
```

### 5.5 `APP_CAPABILITIES_JSON`

Use this for any capability that doesn't have a dedicated field:

```env
APP_CAPABILITIES_JSON={"autoGrantPermissions": true, "language": "en", "locale": "US"}
```

Capabilities in this JSON are merged **last**, so they can override any field-derived capability.

---

## 6. Built-in fixtures

All fixtures are provided automatically by the plugin — no imports required in test files.

### `settings` — session scope

Resolved `AppiumPytestKitSettings` instance, available for the entire test session.

```python
def test_platform_is_android(settings):
    assert settings.platform == "android"
    assert settings.appium_url == "http://127.0.0.1:4723"
```

Access any setting field directly:

```python
def test_check_config(settings):
    print(settings.app_package)
    print(settings.device_name)
    print(settings.capabilities_json)
```

### `appium_server` — session scope

Resolved server descriptor. Has two fields:

| Field | Type | Description |
|---|---|---|
| `url` | `str` | The Appium server URL tests will connect to |
| `managed` | `bool` | `True` if the framework started the server |

```python
def test_server_is_reachable(appium_server):
    assert appium_server.url.startswith("http")
    assert isinstance(appium_server.managed, bool)
```

When `APP_MANAGE_APPIUM_SERVER=true`, the framework starts a local Appium process and tears it down after the session. When `false`, it uses `APP_APPIUM_URL` directly.

### `driver` — function scope

A live `appium.webdriver.Remote` instance. Created fresh for each test, quit automatically after — even on failure.

```python
@pytest.mark.integration
def test_app_launches(driver):
    assert driver.session_id is not None
```

The driver has the full Appium WebDriver API available. Use it to find elements, interact with the UI, take screenshots, etc.

```python
from appium.webdriver.common.appiumby import AppiumBy

@pytest.mark.integration
def test_find_element(driver):
    el = driver.find_element(AppiumBy.ID, "com.example.app:id/button")
    assert el.is_displayed()
```

### `waiter` — function scope

A `Waiter` instance tied to the current `driver`. Provides explicit waits with `WaitTimeoutError` on failure instead of raw Selenium exceptions.

```python
from appium.webdriver.common.appiumby import AppiumBy

@pytest.mark.integration
def test_wait_for_element(waiter):
    locator = (AppiumBy.ID, "com.example.app:id/title")

    # wait up to 10 seconds (default) for presence
    element = waiter.for_presence(locator)

    # wait up to 10 seconds for visibility
    element = waiter.for_visibility(locator)

    # custom timeout
    element = waiter.for_visibility(locator, timeout=20.0)

    # custom condition
    from selenium.webdriver.support import expected_conditions as EC
    element = waiter.until(EC.element_to_be_clickable(locator), timeout=5.0)
```

`Waiter` methods:

| Method | Description |
|---|---|
| `for_presence(locator, *, timeout)` | Wait for element to exist in the DOM |
| `for_visibility(locator, *, timeout)` | Wait for element to be visible |
| `until(condition, *, timeout, message)` | Wait for any custom Selenium `expected_conditions` |

All methods raise `WaitTimeoutError` on timeout.

### `actions` — function scope

A `MobileActions` instance with high-level interaction helpers. Built on top of `waiter`.

```python
from appium.webdriver.common.appiumby import AppiumBy

@pytest.mark.integration
def test_login_flow(actions):
    username = (AppiumBy.ID, "com.example.app:id/username")
    password = (AppiumBy.ID, "com.example.app:id/password")
    login_btn = (AppiumBy.ID, "com.example.app:id/login")
    welcome    = (AppiumBy.ID, "com.example.app:id/welcome_text")

    actions.type_text(username, "testuser")
    actions.type_text(password, "secret", clear_first=True)
    actions.tap(login_btn)

    assert actions.text(welcome) == "Welcome, testuser"
```

`MobileActions` methods:

| Method | Signature | Description |
|---|---|---|
| `tap` | `(locator, *, timeout=10.0)` | Tap a visible element |
| `type_text` | `(locator, value, *, clear_first=True, timeout=10.0)` | Clear (optional) and type into an element |
| `text` | `(locator, *, timeout=10.0)` | Read and return the text content of an element |
| `exists` | `(locator, *, timeout=2.0)` | Return `True` if the element appears within the timeout, `False` otherwise |

All methods raise `ActionError` on Selenium failures (wrapping the underlying `WebDriverException`).

---

## 7. Writing your first test

### Smoke test (no device needed)

The `settings` fixture is always available even without a device. Use it for configuration validation:

```python
# tests/test_config.py

def test_platform_is_configured(settings):
    assert settings.platform in {"android", "ios"}

def test_appium_url_is_set(settings):
    assert settings.appium_url.startswith("http")
    assert "4723" in settings.appium_url
```

Run with:

```bash
pytest tests/test_config.py -v
```

### Integration test (requires device)

```python
# tests/test_smoke.py
import pytest

@pytest.mark.integration
def test_driver_session_opens(driver):
    assert driver.session_id is not None

@pytest.mark.integration
def test_app_title_is_visible(waiter):
    from appium.webdriver.common.appiumby import AppiumBy
    element = waiter.for_visibility((AppiumBy.ID, "com.example.app:id/title"))
    assert element.is_displayed()
```

Run integration tests:

```bash
pytest -m integration -v
```

---

## 8. Step-by-step: testing a real Android app

This example tests the stock **Android Calculator** app available on every Android emulator.

### Step 1 — Start an Android emulator

```bash
# list available AVDs
emulator -list-avds

# start one (replace with your AVD name)
emulator -avd Pixel_7_API_33 &

# verify it is connected
adb devices
# output: emulator-5554   device
```

### Step 2 — Start Appium

```bash
appium
# Appium listening on http://127.0.0.1:4723
```

### Step 3 — Configure `.env`

```env
APP_PLATFORM=android
APP_APPIUM_URL=http://127.0.0.1:4723
APP_DEVICE_NAME=emulator-5554
APP_PLATFORM_VERSION=13
APP_APP_PACKAGE=com.google.android.calculator
APP_APP_ACTIVITY=com.android.calculator2.Calculator
APP_NO_RESET=true
```

> `APP_NO_RESET=true` skips clearing app state between tests, which is fine for the Calculator since it has no login state.

### Step 4 — Create the project structure

```
calculator-tests/
├── .env
├── conftest.py
├── pytest.ini
└── tests/
    └── test_calculator.py
```

`pytest.ini`:

```ini
[pytest]
addopts = -ra --strict-markers
markers =
    integration: requires Appium and a connected device
```

### Step 5 — Define locators in `conftest.py`

Keep locators in one place so tests stay readable:

```python
# conftest.py
from appium.webdriver.common.appiumby import AppiumBy

# Calculator button locators (resource-id on stock Android emulator)
BTN_0  = (AppiumBy.ACCESSIBILITY_ID, "0")
BTN_1  = (AppiumBy.ACCESSIBILITY_ID, "1")
BTN_2  = (AppiumBy.ACCESSIBILITY_ID, "2")
BTN_3  = (AppiumBy.ACCESSIBILITY_ID, "3")
BTN_4  = (AppiumBy.ACCESSIBILITY_ID, "4")
BTN_5  = (AppiumBy.ACCESSIBILITY_ID, "5")
BTN_6  = (AppiumBy.ACCESSIBILITY_ID, "6")
BTN_7  = (AppiumBy.ACCESSIBILITY_ID, "7")
BTN_8  = (AppiumBy.ACCESSIBILITY_ID, "8")
BTN_9  = (AppiumBy.ACCESSIBILITY_ID, "9")
BTN_PLUS   = (AppiumBy.ACCESSIBILITY_ID, "plus")
BTN_MINUS  = (AppiumBy.ACCESSIBILITY_ID, "minus")
BTN_TIMES  = (AppiumBy.ACCESSIBILITY_ID, "multiply")
BTN_DIVIDE = (AppiumBy.ACCESSIBILITY_ID, "divide")
BTN_EQUALS = (AppiumBy.ACCESSIBILITY_ID, "equals")
BTN_CLEAR  = (AppiumBy.ACCESSIBILITY_ID, "clear")

RESULT_DISPLAY = (AppiumBy.RESOURCE_ID, "com.google.android.calculator:id/result_final")
FORMULA_DISPLAY = (AppiumBy.RESOURCE_ID, "com.google.android.calculator:id/result_preview")
```

### Step 6 — Write the tests

```python
# tests/test_calculator.py
import pytest
import conftest as loc


@pytest.mark.integration
class TestCalculatorBasicOperations:

    def test_addition(self, actions):
        """2 + 3 = 5"""
        actions.tap(loc.BTN_2)
        actions.tap(loc.BTN_PLUS)
        actions.tap(loc.BTN_3)
        actions.tap(loc.BTN_EQUALS)

        result = actions.text(loc.RESULT_DISPLAY)
        assert result == "5"

    def test_subtraction(self, actions):
        """9 - 4 = 5"""
        actions.tap(loc.BTN_CLEAR)
        actions.tap(loc.BTN_9)
        actions.tap(loc.BTN_MINUS)
        actions.tap(loc.BTN_4)
        actions.tap(loc.BTN_EQUALS)

        result = actions.text(loc.RESULT_DISPLAY)
        assert result == "5"

    def test_multiplication(self, actions):
        """3 × 4 = 12"""
        actions.tap(loc.BTN_CLEAR)
        actions.tap(loc.BTN_3)
        actions.tap(loc.BTN_TIMES)
        actions.tap(loc.BTN_4)
        actions.tap(loc.BTN_EQUALS)

        result = actions.text(loc.RESULT_DISPLAY)
        assert result == "12"

    def test_division(self, actions):
        """8 ÷ 2 = 4"""
        actions.tap(loc.BTN_CLEAR)
        actions.tap(loc.BTN_8)
        actions.tap(loc.BTN_DIVIDE)
        actions.tap(loc.BTN_2)
        actions.tap(loc.BTN_EQUALS)

        result = actions.text(loc.RESULT_DISPLAY)
        assert result == "4"

    def test_clear_resets_display(self, actions):
        """CLR clears the formula and result."""
        actions.tap(loc.BTN_5)
        actions.tap(loc.BTN_PLUS)
        actions.tap(loc.BTN_5)
        actions.tap(loc.BTN_CLEAR)

        assert not actions.exists(loc.RESULT_DISPLAY, timeout=1.0)
```

### Step 7 — Run the tests

```bash
pytest -m integration -v
```

Expected output:

```
tests/test_calculator.py::TestCalculatorBasicOperations::test_addition       PASSED
tests/test_calculator.py::TestCalculatorBasicOperations::test_subtraction    PASSED
tests/test_calculator.py::TestCalculatorBasicOperations::test_multiplication PASSED
tests/test_calculator.py::TestCalculatorBasicOperations::test_division       PASSED
tests/test_calculator.py::TestCalculatorBasicOperations::test_clear_resets_display PASSED
```

### Step 8 — Run with CLI overrides (no `.env` changes needed)

```bash
# target a different device
pytest -m integration --app-udid emulator-5556

# run with verbose Appium logging
pytest -m integration --app-override APP_APPIUM_SERVER_ARGS="--log-level debug"

# enable JSON report
pytest -m integration --app-reporting-enabled
# report written to: artifacts/appium-pytest-kit/summary.json
```

---

## 9. Step-by-step: testing a real iOS app

### Prerequisites

- macOS with Xcode installed
- A simulator running (`open -a Simulator`)
- `xcuitest` driver installed (`appium driver install xcuitest`)

### `.env` for iOS

```env
APP_PLATFORM=ios
APP_APPIUM_URL=http://127.0.0.1:4723
APP_DEVICE_NAME=iPhone 15
APP_PLATFORM_VERSION=17.0
APP_BUNDLE_ID=com.apple.Preferences
APP_NO_RESET=true
```

### Example test

```python
# tests/test_settings_app.py
import pytest
from appium.webdriver.common.appiumby import AppiumBy


SETTINGS_TITLE = (AppiumBy.ACCESSIBILITY_ID, "Settings")
GENERAL_ROW    = (AppiumBy.ACCESSIBILITY_ID, "General")


@pytest.mark.integration
def test_settings_app_launches(driver):
    assert driver.session_id is not None


@pytest.mark.integration
def test_general_row_is_visible(waiter):
    element = waiter.for_visibility(GENERAL_ROW, timeout=15.0)
    assert element.is_displayed()


@pytest.mark.integration
def test_navigate_to_general(actions):
    actions.tap(GENERAL_ROW)
    about_row = (AppiumBy.ACCESSIBILITY_ID, "About")
    assert actions.exists(about_row)
```

---

## 10. Extension hooks

Implement these in your project's `conftest.py` or in a separate pytest plugin to customise framework behaviour without modifying it.

### `pytest_appium_pytest_kit_configure_settings`

Called once at session start. Return a modified settings object to replace the one loaded from `.env`.

```python
# conftest.py
def pytest_appium_pytest_kit_configure_settings(settings):
    """Force implicit_wait to 2s regardless of .env."""
    return settings.model_copy(update={"implicit_wait": 2.0})
```

- Uses `firstresult=True` — only the first non-`None` return value is used.
- Return `None` (or omit a return) to leave settings unchanged.

### `pytest_appium_pytest_kit_capabilities`

Called before each driver session. Return a dict of additional capabilities to merge in.

```python
# conftest.py
def pytest_appium_pytest_kit_capabilities(capabilities, settings):
    """Add locale and auto-grant permissions for Android."""
    if settings.platform == "android":
        return {
            "autoGrantPermissions": True,
            "language": "en",
            "locale": "US",
        }
```

- All returning implementations are collected and merged in order.
- Return `None` to add nothing.

### `pytest_appium_pytest_kit_driver_created`

Called immediately after each driver session is created. Use it for post-creation setup.

```python
# conftest.py
def pytest_appium_pytest_kit_driver_created(driver, settings):
    """Lock orientation to portrait for all tests."""
    driver.orientation = "PORTRAIT"
```

- Return value is ignored.
- Exceptions propagate and will fail the test.

---

## 11. Custom capabilities adapter

`CapabilitiesAdapter` is a `Protocol` (structural subtype — no inheritance required) for reusable capability transformations that can be passed into `build_driver_config` programmatically.

```python
from collections.abc import Mapping
from typing import Any
from appium_pytest_kit.driver import build_driver_config
from appium_pytest_kit.interfaces import CapabilitiesAdapter
from appium_pytest_kit.settings import AppiumPytestKitSettings


class StagingCapabilitiesAdapter:
    """Add staging-environment specific capabilities."""

    def adapt(
        self,
        capabilities: Mapping[str, Any],
        settings: AppiumPytestKitSettings,
    ) -> Mapping[str, Any]:
        caps = dict(capabilities)
        caps["customEnv"] = "staging"
        caps["autoGrantPermissions"] = True
        return caps


# Use it when building a config manually:
settings = AppiumPytestKitSettings()
config = build_driver_config(settings, adapters=[StagingCapabilitiesAdapter()])
```

Multiple adapters are applied in order — each receives the output of the previous.

---

## 12. Managed Appium server

When `APP_MANAGE_APPIUM_SERVER=true`, the framework spawns a local Appium process before the first test and stops it after the session. This is useful for CI environments where you don't want to manage Appium separately.

```env
APP_MANAGE_APPIUM_SERVER=true
APP_APPIUM_HOST=127.0.0.1
APP_APPIUM_PORT=4723
APP_APPIUM_BASE_PATH=/
APP_APPIUM_START_TIMEOUT=30.0
# extra args passed to the appium CLI, comma-separated:
APP_APPIUM_SERVER_ARGS=--log-level warn,--relaxed-security
```

Or via CLI:

```bash
pytest --app-manage-appium-server
```

Requirements:
- `appium` must be on `PATH`
- `Appium-Python-Client>=4.0.0` must be installed (already a dependency)

---

## 13. Reporting

Enable the built-in JSON report:

```env
APP_REPORTING_ENABLED=true
APP_REPORT_DIR=artifacts/appium-pytest-kit
```

After the session, `artifacts/appium-pytest-kit/summary.json` is written:

```json
{
  "totals": {
    "passed": 4,
    "failed": 1,
    "skipped": 0
  },
  "tests": [
    {
      "nodeid": "tests/test_calculator.py::TestCalculatorBasicOperations::test_addition",
      "outcome": "passed",
      "duration": 3.142
    },
    {
      "nodeid": "tests/test_calculator.py::TestCalculatorBasicOperations::test_division",
      "outcome": "failed",
      "duration": 2.891
    }
  ]
}
```

Only the `call` phase is recorded (setup/teardown failures are not counted).

---

## 14. Public API reference

### `AppiumPytestKitSettings`

```python
from appium_pytest_kit import AppiumPytestKitSettings

settings = AppiumPytestKitSettings(platform="android", app_package="com.example")
settings = AppiumPytestKitSettings(_env_file="path/to/.env")
```

All fields described in [Section 5.2](#52-all-settings). Validated by pydantic on construction.

### `load_settings`

```python
from appium_pytest_kit import load_settings

settings = load_settings()                      # reads .env in cwd
settings = load_settings(env_file="ci.env")    # custom path
```

### `apply_cli_overrides`

```python
from appium_pytest_kit import apply_cli_overrides

settings = load_settings()
settings = apply_cli_overrides(settings, {"APP_PLATFORM": "ios", "implicit_wait": 2.0})
```

Returns a new `AppiumPytestKitSettings` instance. Does not mutate the original.

### `DriverConfig`

Immutable dataclass holding the resolved connection details passed to `create_driver`.

```python
from appium_pytest_kit import DriverConfig

config = DriverConfig(
    server_url="http://127.0.0.1:4723",
    capabilities={"platformName": "android", ...},
    implicit_wait=0.0,
)
```

### `build_driver_config`

```python
from appium_pytest_kit import build_driver_config

config = build_driver_config(settings)
config = build_driver_config(settings, server_url="http://remote:4723")
config = build_driver_config(settings, adapters=[MyAdapter()])
```

Builds a `DriverConfig` from `AppiumPytestKitSettings` and an optional list of `CapabilitiesAdapter`.

### `create_driver`

```python
from appium_pytest_kit import create_driver

driver = create_driver(config)   # returns appium.webdriver.Remote
driver.quit()
```

Creates a live Appium session. Raises `DriverCreationError` on failure.

### `Waiter`

```python
from appium_pytest_kit import Waiter

waiter = Waiter(driver, default_timeout=15.0, poll_frequency=0.5)
element = waiter.for_presence(locator)
element = waiter.for_visibility(locator, timeout=5.0)
element = waiter.until(some_condition, timeout=10.0, message="not found")
```

### `MobileActions`

```python
from appium_pytest_kit import MobileActions

actions = MobileActions(driver=driver, waiter=waiter)
actions.tap(locator)
actions.type_text(locator, "hello", clear_first=True)
text = actions.text(locator)
found = actions.exists(locator, timeout=2.0)
```

### `CapabilitiesAdapter` (Protocol)

```python
from appium_pytest_kit.interfaces import CapabilitiesAdapter

class MyAdapter:                               # no inheritance needed
    def adapt(self, capabilities, settings):
        return {**capabilities, "myKey": "myValue"}

assert isinstance(MyAdapter(), CapabilitiesAdapter)  # runtime check works
```

---

## 15. Error hierarchy

```
Exception
└── AppiumPytestKitError       base for all framework errors
    ├── ConfigurationError     invalid settings, managed server failed to start
    ├── WaitTimeoutError       explicit wait timed out
    ├── ActionError            tap / type_text / text raised WebDriverException
    └── DriverCreationError    Appium session could not be created
```

Catch the base class to handle any framework error:

```python
from appium_pytest_kit import AppiumPytestKitError

try:
    actions.tap(locator)
except AppiumPytestKitError as exc:
    print(f"Framework error: {exc}")
```

Or catch specific subclasses for fine-grained handling:

```python
from appium_pytest_kit import WaitTimeoutError, ActionError

try:
    actions.tap(locator, timeout=5.0)
except WaitTimeoutError:
    pytest.skip("Element did not appear — skipping")
except ActionError as exc:
    pytest.fail(f"Tap failed: {exc}")
```

---

## 16. Project structure

```
src/appium_pytest_kit/
├── __init__.py             # public API surface
├── _version.py             # version via importlib.metadata
├── py.typed                # PEP 561 marker (typed package)
│
├── settings.py             # AppiumPytestKitSettings + load/override helpers
├── driver.py               # DriverConfig, build_driver_config, create_driver
├── waits.py                # Waiter, Locator type alias
├── actions.py              # MobileActions
├── errors.py               # Exception hierarchy
├── interfaces.py           # CapabilitiesAdapter Protocol
├── hooks.py                # AppiumPytestKitHookSpecs (pytest hook specs)
├── pytest_plugin.py        # Fixtures + pytest hooks (registered via entry point)
│
└── _internal/              # Private — no compatibility guarantee
    ├── __init__.py
    ├── server.py           # AppiumServerManager (managed server lifecycle)
    └── reporting.py        # SessionReportCollector (JSON report)
```

---

## 17. Troubleshooting

### `DriverCreationError: Failed to create Appium session`

- Is Appium running? `curl http://127.0.0.1:4723/status`
- Does `APP_APPIUM_URL` match where Appium is listening?
- Is the device connected? `adb devices` (Android) or check Simulator is open (iOS)

### `ConfigurationError: Failed to start managed Appium server`

- Is `appium` on `PATH`? Run `which appium`
- Try increasing `APP_APPIUM_START_TIMEOUT=45.0`
- Check Appium logs for the actual error

### `WaitTimeoutError: Element not visible`

- Check the locator strategy — use Appium Inspector to find correct IDs
- The app may not have launched yet — increase `APP_NEW_COMMAND_TIMEOUT`
- Increase the wait timeout: `waiter.for_visibility(locator, timeout=30.0)`

### Settings are not being picked up from `.env`

- The `.env` file must be in the directory where `pytest` is invoked
- Or specify it explicitly: `pytest --app-env-file /full/path/.env`
- Variable names must be prefixed with `APP_` (e.g. `APP_PLATFORM`, not `PLATFORM`)

### `platform must be 'android' or 'ios'`

- `APP_PLATFORM` only accepts exactly `android` or `ios` (case-insensitive)

### Tests pass locally but fail in CI

- Verify `APP_UDID` matches the CI emulator: `adb devices` in the CI step
- Add `--app-reporting-enabled` to get a JSON summary artifact
- Pin emulator API level to avoid version drift between `APP_PLATFORM_VERSION` and the running emulator
