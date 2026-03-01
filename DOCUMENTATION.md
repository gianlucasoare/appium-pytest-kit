# appium-pytest-kit — Documentation

## Quick navigation

| I want to… | Go to |
|---|---|
| Install the library | [Installation →](docs/installation.md) |
| Set up a new project | [Project structure →](docs/project-structure.md) |
| Configure my device and app | [Configuration →](docs/configuration.md) |
| See every CLI flag in one place | [CLI reference →](docs/cli-reference.md) |
| Understand the built-in fixtures | [Fixtures →](docs/fixtures.md) |
| Build page object classes | [Page objects guide →](docs/page-objects.md) |
| Build flow objects (multi-page journeys) | [Page objects guide →](docs/page-objects.md) |
| Know what to put in `conftest.py` | [conftest guide →](docs/conftest-guide.md) |
| Look up wait methods | [Waits reference →](docs/waits.md) |
| Look up action methods | [Actions reference →](docs/actions.md) |
| Choose a session mode | [Session modes →](docs/session-modes.md) |
| Set up device targeting | [Device resolution →](docs/device-resolution.md) |
| Learn API testing step by step | [API testing →](docs/api-testing.md) |
| Configure screenshots/video | [Diagnostics →](docs/diagnostics.md) |
| Handle errors in tests | [Errors →](docs/errors.md) |
| Fix a problem | [Troubleshooting →](docs/troubleshooting.md) |

---

## Step-by-step: new user starting from scratch

If you're brand new, follow these steps in order:

1. **[Install](docs/installation.md)** — Python venv, Appium 2, the kit
2. **[Scaffold the project](docs/project-structure.md)** — `appium-pytest-kit-init --framework`
3. **[Configure `.env`](docs/configuration.md)** — device + app details
4. **Run the smoke test** — `pytest tests/android/test_smoke.py -v`
5. **[Build your first page object](docs/page-objects.md)** — `pages/login_page.py`
6. **[Write your first real test](docs/conftest-guide.md)** — `conftest.py` + test file
7. **[Add API endpoint tests](docs/api-testing.md)** — backend checks + hybrid API/UI flows

---

## Step-by-step: testing a real Android app

### Prerequisites

- Python 3.11+ with a virtual environment
- `appium-pytest-kit` installed (`pip install appium-pytest-kit`)
- Appium 2 installed (`npm install -g appium`)
- UiAutomator2 driver (`appium driver install uiautomator2`)
- Android SDK with `adb` on PATH
- A connected device or running emulator

### Step 1 — Start Appium and an emulator

```bash
# List available AVDs
emulator -list-avds

# Start one
emulator -avd Pixel_7_API_34 &

# Confirm it's connected
adb devices
# emulator-5554   device
```

```bash
# Start Appium
appium
# Appium HTTP listening on http://0.0.0.0:4723
```

### Step 2 — Scaffold the project

```bash
appium-pytest-kit-init --framework --root calculator-tests
cd calculator-tests
```

### Step 3 — Configure `.env`

Edit the generated `.env` file:

```env
APP_PLATFORM=android
APP_APPIUM_URL=http://127.0.0.1:4723
APP_DEVICE_NAME=emulator-5554
APP_PLATFORM_VERSION=14
APP_APP_PACKAGE=com.google.android.calculator
APP_APP_ACTIVITY=com.android.calculator2.Calculator
APP_NO_RESET=true
APP_EXPLICIT_WAIT_TIMEOUT=10
```

### Step 4 — Create the calculator page object

```python
# pages/calculator_page.py
from appium.webdriver.common.appiumby import AppiumBy
from appium_pytest_kit import Locator
from pages.base_page import BasePage


class CalculatorPage(BasePage):
    # ── locators ──────────────────────────────────────────────────────────
    _BTN_0: Locator = (AppiumBy.ACCESSIBILITY_ID, "0")
    _BTN_1: Locator = (AppiumBy.ACCESSIBILITY_ID, "1")
    _BTN_2: Locator = (AppiumBy.ACCESSIBILITY_ID, "2")
    _BTN_3: Locator = (AppiumBy.ACCESSIBILITY_ID, "3")
    _BTN_4: Locator = (AppiumBy.ACCESSIBILITY_ID, "4")
    _BTN_5: Locator = (AppiumBy.ACCESSIBILITY_ID, "5")
    _BTN_6: Locator = (AppiumBy.ACCESSIBILITY_ID, "6")
    _BTN_7: Locator = (AppiumBy.ACCESSIBILITY_ID, "7")
    _BTN_8: Locator = (AppiumBy.ACCESSIBILITY_ID, "8")
    _BTN_9: Locator = (AppiumBy.ACCESSIBILITY_ID, "9")
    _BTN_PLUS: Locator = (AppiumBy.ACCESSIBILITY_ID, "plus")
    _BTN_MINUS: Locator = (AppiumBy.ACCESSIBILITY_ID, "minus")
    _BTN_TIMES: Locator = (AppiumBy.ACCESSIBILITY_ID, "multiply")
    _BTN_DIVIDE: Locator = (AppiumBy.ACCESSIBILITY_ID, "divide")
    _BTN_EQUALS: Locator = (AppiumBy.ACCESSIBILITY_ID, "equals")
    _BTN_CLEAR: Locator = (AppiumBy.ACCESSIBILITY_ID, "clear")
    _RESULT: Locator = (
        AppiumBy.RESOURCE_ID,
        "com.google.android.calculator:id/result_final",
    )

    # ── load check ────────────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        return self._actions.is_displayed(self._BTN_0)

    # ── button helpers ────────────────────────────────────────────────────

    def _digit(self, n: int) -> None:
        buttons = {
            0: self._BTN_0, 1: self._BTN_1, 2: self._BTN_2, 3: self._BTN_3,
            4: self._BTN_4, 5: self._BTN_5, 6: self._BTN_6, 7: self._BTN_7,
            8: self._BTN_8, 9: self._BTN_9,
        }
        self._actions.tap(buttons[n])

    def clear(self) -> None:
        self._actions.tap(self._BTN_CLEAR)

    # ── operations ────────────────────────────────────────────────────────

    def add(self, a: int, b: int) -> None:
        self._digit(a)
        self._actions.tap(self._BTN_PLUS)
        self._digit(b)
        self._actions.tap(self._BTN_EQUALS)

    def subtract(self, a: int, b: int) -> None:
        self._digit(a)
        self._actions.tap(self._BTN_MINUS)
        self._digit(b)
        self._actions.tap(self._BTN_EQUALS)

    def multiply(self, a: int, b: int) -> None:
        self._digit(a)
        self._actions.tap(self._BTN_TIMES)
        self._digit(b)
        self._actions.tap(self._BTN_EQUALS)

    def divide(self, a: int, b: int) -> None:
        self._digit(a)
        self._actions.tap(self._BTN_DIVIDE)
        self._digit(b)
        self._actions.tap(self._BTN_EQUALS)

    # ── read ──────────────────────────────────────────────────────────────

    def result(self) -> str:
        return self._actions.text(self._RESULT)
```

### Step 5 — Add a conftest fixture

```python
# conftest.py
import pytest
from pages.calculator_page import CalculatorPage


@pytest.fixture
def calculator(page_factory):
    calc = page_factory(CalculatorPage)
    calc.is_loaded()  # wait for the app to be ready
    return calc
```

### Step 6 — Write the tests

```python
# tests/android/test_calculator.py
import pytest


@pytest.mark.integration
class TestCalculatorOperations:

    def test_addition(self, calculator):
        calculator.clear()
        calculator.add(2, 3)
        assert calculator.result() == "5"

    def test_subtraction(self, calculator):
        calculator.clear()
        calculator.subtract(9, 4)
        assert calculator.result() == "5"

    def test_multiplication(self, calculator):
        calculator.clear()
        calculator.multiply(3, 4)
        assert calculator.result() == "12"

    def test_division(self, calculator):
        calculator.clear()
        calculator.divide(8, 2)
        assert calculator.result() == "4"
```

### Step 7 — Run the tests

```bash
pytest -m integration -v
```

Expected output:

```
tests/android/test_calculator.py::TestCalculatorOperations::test_addition        PASSED
tests/android/test_calculator.py::TestCalculatorOperations::test_subtraction     PASSED
tests/android/test_calculator.py::TestCalculatorOperations::test_multiplication  PASSED
tests/android/test_calculator.py::TestCalculatorOperations::test_division        PASSED
```

### Step 8 — Enable failure artifacts

```bash
pytest -m integration --app-video-policy failed -v
```

On any failure, `artifacts/screenshots/` and `artifacts/pagesource/` will contain the evidence automatically.

---

## Step-by-step: testing a real iOS app

### Prerequisites

- macOS with Xcode 14+ installed
- Appium XCUITest driver: `appium driver install xcuitest`
- A booted iOS Simulator: `open -a Simulator`

### Step 1 — Configure `.env` for iOS

```env
APP_PLATFORM=ios
APP_APPIUM_URL=http://127.0.0.1:4723
APP_DEVICE_NAME=iPhone 15 Pro
APP_PLATFORM_VERSION=17.4
APP_BUNDLE_ID=com.apple.Preferences
APP_IS_SIMULATOR=true
APP_NO_RESET=true
APP_EXPLICIT_WAIT_TIMEOUT=15
```

### Step 2 — Create a page object for the Settings app

```python
# pages/settings_page.py
from appium.webdriver.common.appiumby import AppiumBy
from appium_pytest_kit import Locator
from pages.base_page import BasePage


class SettingsPage(BasePage):
    _SEARCH: Locator = (AppiumBy.ACCESSIBILITY_ID, "Search")
    _GENERAL_ROW: Locator = (AppiumBy.ACCESSIBILITY_ID, "General")
    _PRIVACY_ROW: Locator = (AppiumBy.ACCESSIBILITY_ID, "Privacy & Security")

    def is_loaded(self, *, timeout: float = 15.0) -> bool:
        return self._actions.is_displayed(self._GENERAL_ROW, timeout=timeout)

    def tap_general(self) -> None:
        self._actions.tap(self._GENERAL_ROW)

    def tap_privacy(self) -> None:
        self._actions.tap(self._PRIVACY_ROW)

    def search(self, query: str) -> None:
        self._actions.tap(self._SEARCH)
        self._actions.type_text(self._SEARCH, query)
```

### Step 3 — Write the tests

```python
# tests/ios/test_settings.py
import pytest
from pages.settings_page import SettingsPage


@pytest.fixture
def settings_app(page_factory):
    page = page_factory(SettingsPage)
    assert page.is_loaded(), "Settings app did not load"
    return page


@pytest.mark.integration
def test_settings_app_launches(settings_app):
    assert settings_app.is_loaded()


@pytest.mark.integration
def test_general_row_is_visible(settings_app):
    # already confirmed by is_loaded(), but check the explicit fixture approach
    settings_app.tap_general()
    # navigate back
    from appium.webdriver.common.appiumby import AppiumBy
    ABOUT_ROW = (AppiumBy.ACCESSIBILITY_ID, "About")
    from appium_pytest_kit import WaitTimeoutError
    # if we can see About, we're in General settings
    assert settings_app._actions.is_displayed(ABOUT_ROW, timeout=10.0)
```

### Step 4 — Run the tests

```bash
# Start Appium first (in another terminal)
appium

# Run
pytest tests/ios/ -m integration -v
```

---

## All settings table

See [docs/configuration.md](docs/configuration.md) for the full settings reference including `APP_EXPLICIT_WAIT_TIMEOUT` and all other options.

---

## Migration notes

### From v0.1.2 → v0.1.3

All existing tests continue to work without changes.

**New optional extra:**
```bash
pip install "appium-pytest-kit[retry]"  # adds pytest-retry
```

**New CLI flags:**
- `--retries N` — retry failed tests N extra times *(requires `[retry]` extra)*
- `--retry-delay SECS` — wait between retry attempts
- `--app-fail-fast` — stop the suite after a test exhausts all retries

**New retry behaviour:**
- During retries the existing Appium session is reused — no session restart between attempts
- After the final failure or a pass, the session is quit and the next test starts fresh (matches `appium-framework-setup` behaviour with `pytest-rerunfailures`)
- Use `@pytest.mark.flaky(retries=N)` per-test or `--retries N` globally (pytest-retry's API)

**New scaffold output:**
- `appium-pytest-kit-init --framework` now generates `flows/base_flow.py` and `flows/example_flow.py` in addition to the existing `flows/__init__.py`

**Bug fix:**
- `--app-explicit-wait-timeout` was documented as a direct CLI flag but does not exist. The correct way to override this at the command line is: `--app-override APP_EXPLICIT_WAIT_TIMEOUT=15`

---

### From pre-v0.1.1

All existing tests continue to work without changes.

**New settings (safe defaults — no action required):**
- `APP_EXPLICIT_WAIT_TIMEOUT` (default `10.0`) — replaces the `max(implicit_wait, 10.0)` floor that was applied internally. If you were relying on the old behaviour, add `APP_EXPLICIT_WAIT_TIMEOUT=10` to `.env`.

**New fixtures:**
- `page_factory` — new, opt-in. Existing tests using raw `driver`/`waiter`/`actions` continue to work.
- `device_info` — new, session-scoped. Safe to ignore if you don't need it.

**New public API:**
- `Locator` type alias exported from `appium_pytest_kit` — add type annotations to page objects
- `DeviceResolutionError`, `LaunchValidationError` — new subclasses of `AppiumPytestKitError`
- `Waiter.default_timeout` property — replaces internal `_default_timeout`

**Behaviour change:**
- `LaunchValidationError` is now raised at driver creation time if required app settings are missing, instead of letting the error surface as a raw Appium exception.
- Multiple connected Android devices now emit a `UserWarning` instead of silently picking the first one.
- Artifact capture failures now emit `UserWarning` instead of being fully silent.

**Optional extras (new):**
```bash
pip install "appium-pytest-kit[yaml]"   # was: pip install PyYAML separately
pip install "appium-pytest-kit[allure]" # was: pip install allure-pytest separately
```
