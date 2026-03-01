# appium-pytest-kit

`appium-pytest-kit` is a reusable Appium 2.x + pytest plugin library for Python 3.11+. Install it once, generate a `.env`, and start writing mobile tests with zero boilerplate.

```bash
pip install appium-pytest-kit
appium-pytest-kit-init --framework --root my-project
```

**Full documentation:** [DOCUMENTATION.md](./DOCUMENTATION.md) · [docs/](./docs/)

---

## What it gives you

| | |
|---|---|
| **Zero-config fixtures** | `driver`, `waiter`, `actions`, `page_factory` — just add to your test function |
| **Auto failure artifacts** | Screenshot + page source + device logs + session log captured automatically on failure |
| **Artifact redaction** | Optional redaction for text artifacts + optional screenshot placeholder mode |
| **3-tier device resolution** | explicit settings → named profile → auto-detect via adb/xcrun |
| **Session modes** | `clean` (per-test) · `clean-session` (shared) · `debug` (keep alive) |
| **Retry support** | Session reused across retry attempts — no restart cost between tries |
| **Flake quality gates** | `scripts/check_flake_thresholds.py` can fail CI when flake budgets are exceeded |
| **Performance checks** | Optional perf telemetry (`perf-summary.json` / `perf-trend.json`) + soft budgets |
| **xdist parallelism** | Worker-safe capability port isolation + per-worker managed Appium ports |
| **Quarantine lane** | `@pytest.mark.quarantine` tests can be isolated from default lanes |
| **Fail-fast** | `--app-fail-fast` stops the suite after retries are exhausted, not before |
| **Explicit waits** | `WaitTimeoutError` with structured `.locator` and `.timeout` context |
| **High-level actions** | tap, type, swipe, scroll, assertions — all wait-safe |
| **App reset primitives** | clear app data, reset permissions, reinstall app helpers in `actions` |
| **Page + flow objects** | Scaffold generates `pages/` and `flows/` with base classes ready to extend |
| **Extension hooks** | Override settings, inject capabilities, run code after driver creation |
| **CLI scaffold** | One command to generate a full project structure |

---

## Dependencies

All required dependencies are **installed automatically** with `pip install appium-pytest-kit`. You do not need a separate `requirements.txt`.

| Auto-installed | Version | Purpose |
|---|---|---|
| `Appium-Python-Client` | ≥ 4.0.0 | Appium WebDriver client |
| `pydantic-settings` | ≥ 2.3.0 | `.env` and env var loading |
| `pytest` | ≥ 8.2.0 | Test runner integration |

**Optional extras** (install only what you need):

```bash
pip install "appium-pytest-kit[yaml]"    # device profile YAML support
pip install "appium-pytest-kit[allure]"  # Allure report attachments
pip install "appium-pytest-kit[retry]"   # pytest-retry for flaky test handling
pip install "appium-pytest-kit[xdist]"   # pytest-xdist parallel execution
pip install "appium-pytest-kit[all]"     # all optional extras
```

| Extra | Installs | When you need it |
|---|---|---|
| `[yaml]` | PyYAML ≥ 6.0 | Named device profiles in `data/devices.yaml` |
| `[allure]` | allure-pytest ≥ 2.13.0 | Screenshots + page source in Allure reports |
| `[retry]` | pytest-retry ≥ 0.6.0 | Retry flaky tests while reusing the same Appium session |
| `[xdist]` | pytest-xdist ≥ 3.6.0 | Run tests in parallel workers safely |

---

## Installation

### From PyPI

```bash
pip install appium-pytest-kit
```

### From GitHub

```bash
pip install git+https://github.com/gianlucasoare/appium-pytest-kit.git
```

### Local clone (development)

```bash
git clone https://github.com/gianlucasoare/appium-pytest-kit.git
cd appium-pytest-kit
pip install -e ".[dev]"
```

### Environment doctor

Validate your local setup (tools, drivers, config, Appium reachability):

```bash
appium-pytest-kit-doctor
appium-pytest-kit-doctor --env-file .env.staging
appium-pytest-kit-doctor --json
```

### Automated PyPI release

The repository includes a GitHub Actions release workflow with Trusted Publishing:
- workflow file: `.github/workflows/release.yml`
- trigger: push a tag like `v0.1.8`
- behavior: run tests, build `sdist` + wheel, verify tag/version match, publish to PyPI via OIDC
- publish guard: `publish` job runs only for `refs/tags/v*`
- optional signed-tag enforcement via `REQUIRE_SIGNED_TAG=true` repo variable
- auto-generated GitHub release notes after publish

Changelog automation is also available via `.github/workflows/changelog.yml`
(`workflow_dispatch`) to generate a release section in `CHANGELOG.md` and open a PR.
CI in `.github/workflows/ci.yml` also validates conventional commit subjects and
runs a dedicated quarantined-test lane (`@pytest.mark.quarantine`).

---

## Quickstart: test an app in 5 minutes

### 1 — Scaffold the project

```bash
pip install appium-pytest-kit
appium-pytest-kit-init --framework --root my-project
cd my-project
```

### 2 — Edit `.env` with your device and app

```env
APP_PLATFORM=android
APP_APPIUM_URL=http://127.0.0.1:4723
APP_APP_PACKAGE=com.example.myapp
APP_APP_ACTIVITY=.MainActivity
APP_DEVICE_NAME=emulator-5554
APP_PLATFORM_VERSION=14
```

### 3 — Start Appium and your emulator, then run

```bash
appium &
pytest tests/android/test_smoke.py -v
```

### 4 — Write a real test

```python
# tests/android/test_login.py
import pytest
from appium.webdriver.common.appiumby import AppiumBy

USERNAME = (AppiumBy.ID, "com.example.app:id/username")
PASSWORD = (AppiumBy.ID, "com.example.app:id/password")
LOGIN_BTN = (AppiumBy.ACCESSIBILITY_ID, "login_button")
WELCOME = (AppiumBy.ID, "com.example.app:id/welcome_text")


@pytest.mark.integration
def test_login(actions):
    actions.type_text(USERNAME, "testuser")
    actions.type_text(PASSWORD, "secret")
    actions.tap(LOGIN_BTN)
    assert actions.text(WELCOME) == "Welcome, testuser"
```

```bash
pytest -m integration -v
```

---

## Built-in fixtures

| Fixture | Scope | Description |
|---|---|---|
| `settings` | session | Resolved `AppiumPytestKitSettings` |
| `device_info` | session | Resolved device (name, UDID, version) |
| `appium_server` | session | Server URL, optional lifecycle management |
| `driver` | function | Live `appium.webdriver.Remote`, auto-quit |
| `waiter` | function | Explicit waits with `WaitTimeoutError` |
| `actions` | function | High-level UI helpers |
| `page_factory` | function | Factory for page objects: `page_factory(LoginPage)` |

---

## Page objects with `page_factory`

```python
# pages/login_page.py
from appium.webdriver.common.appiumby import AppiumBy
from appium_pytest_kit import Locator
from pages.base_page import BasePage

class LoginPage(BasePage):
    _USERNAME: Locator = (AppiumBy.ID, "com.example.app:id/username")
    _LOGIN_BTN: Locator = (AppiumBy.ACCESSIBILITY_ID, "login_button")

    def log_in(self, username: str, password: str) -> None:
        self._actions.type_text(self._USERNAME, username)
        self._actions.tap(self._LOGIN_BTN)

    def is_loaded(self) -> bool:
        return self._actions.is_displayed(self._USERNAME)
```

```python
# tests/test_login.py
def test_login_success(page_factory):
    login = page_factory(LoginPage)
    login.wait_until_loaded()
    login.log_in("testuser", "secret")
    # ...
```

See [docs/page-objects.md](docs/page-objects.md) for the full guide.

---

## Session modes

```env
APP_SESSION_MODE=clean          # fresh driver per test (default)
APP_SESSION_MODE=clean-session  # one shared driver for the whole run (faster)
APP_SESSION_MODE=debug          # shared + no restart on failure (local debugging)
```

---

## Retry support

Install the extra, then use `@pytest.mark.flaky(...)` and/or the `--retries` CLI flag:

```bash
pip install "appium-pytest-kit[retry]"
```

```python
# Retry this test up to 2 extra times (3 total attempts)
@pytest.mark.flaky(retries=2)
def test_flaky_animation(actions):
    actions.tap(START_BTN)
    actions.assert_displayed(RESULT_SCREEN)
```

```bash
# Retry every failed test up to 2 extra times, stop if something is truly broken
pytest --retries 2 --retry-delay 1 --app-fail-fast
```

**How it works:** during retries the same Appium session is reused — no restart between attempts. Once the test passes or all retries are exhausted, the session is quit and the next test starts fresh.

See [docs/cli-reference.md](docs/cli-reference.md) for the full retry flag reference.

---

## Parallel with xdist

Install xdist support:

```bash
pip install "appium-pytest-kit[xdist]"
```

Run tests in parallel workers:

```bash
pytest -n 4
```

When running with xdist:
- Android workers get default `systemPort` values (`8200 + worker_index`) unless explicitly set.
- iOS workers get default `wdaLocalPort` (`8100 + worker_index`) and `webkitDebugProxyPort` (`27753 + worker_index`) unless explicitly set.
- With `APP_MANAGE_APPIUM_SERVER=true`, each worker starts Appium on `APP_APPIUM_PORT + worker_index`.

---

## Device resolution (3-tier)

1. **Explicit** — `APP_DEVICE_NAME` / `APP_UDID` in `.env` or CLI
2. **Profile** — `APP_DEVICE_PROFILE=pixel7` from `data/devices.yaml`
3. **Auto-detect** — `adb devices` (Android) or `xcrun simctl` / `xctrace` (iOS)

```bash
pytest --app-device-profile pixel7
pytest --app-udid emulator-5554
pytest   # auto-detect if nothing set
```

---

## Failure diagnostics

On test failure the framework automatically captures:
- **Screenshot** → `artifacts/screenshots/<test_id>.png`
- **Page source** → `artifacts/pagesource/<test_id>.xml`
- **Device logs** → `artifacts/device_logs/<test_id>.log`
- **Session log** → `artifacts/session_logs/<test_id>.log` (from available Appium log type)
- **Video** (if configured) → `artifacts/videos/<test_id>.mp4`

```env
APP_VIDEO_POLICY=failed   # record and save only on failure
APP_VIDEO_POLICY=always   # record every test
```

Allure attachments are added automatically when `allure-pytest` is installed.

---

## Configuration

Settings load from `.env` → env vars → CLI flags (highest wins).

```bash
pytest --app-platform ios
pytest --app-device-name "Pixel 7" --app-platform-version 14
pytest --app-appium-url http://192.168.1.10:4723
pytest --app-session-mode clean-session
pytest --app-device-profile pixel7
pytest --app-video-policy failed
pytest --app-override APP_EXPLICIT_WAIT_TIMEOUT=15
pytest --app-capabilities-json '{"autoGrantPermissions": true}'
pytest --app-strict-config
pytest --app-manage-appium-server
pytest --app-reporting-enabled

# Retry support (requires appium-pytest-kit[retry])
pytest --retries 2 --retry-delay 1          # retry all tests up to 2 extra times
pytest --retries 2 --app-fail-fast          # stop suite after retries are exhausted
```

See [docs/configuration.md](docs/configuration.md) for all settings.

---

## Extension hooks

```python
# conftest.py

def pytest_appium_pytest_kit_capabilities(capabilities, settings):
    """Add extra capabilities before each driver session."""
    if settings.platform == "android":
        return {"autoGrantPermissions": True, "language": "en"}

def pytest_appium_pytest_kit_configure_settings(settings):
    """Replace settings at session start."""
    return settings.model_copy(update={"explicit_wait_timeout": 20.0})

def pytest_appium_pytest_kit_driver_created(driver, settings):
    """Run setup immediately after each driver is created."""
    driver.orientation = "PORTRAIT"
```

---

## Expanded waits

```python
waiter.for_clickable(locator)
waiter.for_invisibility(locator)
waiter.for_text_contains(locator, "partial text")
waiter.for_text_equals(locator, "exact text")
waiter.for_all_visible([loc1, loc2, loc3])   # single timeout for the whole group
waiter.for_all_gone([loc1, loc2])
waiter.for_any_visible([loc1, loc2])
waiter.for_context_contains("WEBVIEW")
waiter.for_android_activity("MainActivity")
waiter.for_android_toast("Saved")
```

---

## Expanded actions

```python
# Tap
actions.tap_if_present(locator)
actions.tap_if_present_first_available([l1, l2])
actions.click_by_attribute_value((By.ID, "toggle"), "checked", "true")
actions.tap_by_coordinates(x, y)
actions.double_tap(locator)
actions.long_press(locator, duration_seconds=2)

# Text
actions.type_if_present(locator, "text")
actions.type_text_slowly(locator, "otp", delay_per_char=0.15)
actions.clear(locator)

# Visibility assertions
actions.is_displayed(locator)
actions.assert_displayed(locator)
actions.is_not_displayed(locator)
actions.assert_not_displayed(locator)
actions.assert_displayed_first_available([l1, l2])
actions.assert_not_displayed_first_available([l1, l2])

# Text assertions
actions.assert_text(locator, "exact text")
actions.assert_text_contains(locator, "partial")
actions.assert_text_not_empty(locator)

# Attribute assertion
actions.assert_attribute(locator, "checked", "true")

# Enabled/disabled state
actions.is_enabled(locator)
actions.assert_enabled(locator)
actions.assert_not_enabled(locator)

# Checked/selected state (checkboxes, toggles)
actions.is_checked(locator)
actions.assert_checked(locator)
actions.assert_not_checked(locator)

# Element count
actions.count(locator)           # → int
actions.assert_count(locator, 3)

# Scroll
actions.scroll_down()
actions.scroll_to_element(locator)

# Keyboard
actions.hide_keyboard()
actions.press_keycode(66)  # ENTER

# App lifecycle
actions.activate_app("com.example.myapp")
actions.terminate_app("com.example.myapp")
actions.background_app(2)
actions.clear_app_data("com.example.myapp")        # Android only
actions.reset_app_permissions()                     # Android only
actions.reinstall_app(app_path="/tmp/build.apk")
actions.open_deep_link("myapp://profile", app_id="com.example.myapp")

# Hybrid
actions.switch_to_webview()
actions.get_webview_context_name()
actions.switch_to_frame("iframe.checkout")
actions.switch_to_default_frame()
actions.switch_to_native()
```

---

## Public API

```python
from appium_pytest_kit import (
    AppiumPytestKitSettings,
    AppiumPytestKitError,
    ConfigurationError, DeviceResolutionError, LaunchValidationError,
    WaitTimeoutError, ActionError, DriverCreationError,
    DeviceInfo, DriverConfig, MobileActions, Waiter,
    Locator,           # type alias: tuple[str, str]
    build_driver_config, create_driver, load_settings, apply_cli_overrides,
)
```

---

## Fixture lifecycle

```mermaid
flowchart TD
    A["pytest start"] --> B["load defaults + .env + env vars"]
    B --> C["apply --app-* CLI overrides"]
    C --> D["settings fixture (session)"]
    D --> E{"APP_MANAGE_APPIUM_SERVER"}
    E -->|"true"| F["start local Appium server"]
    E -->|"false"| G["use APP_APPIUM_URL"]
    F --> H["appium_server fixture (session)"]
    G --> H
    H --> I{"session_mode"}
    I -->|"clean-session / debug"| J["_driver_shared (session)"]
    I -->|"clean"| K["driver per test"]
    J --> K
    K --> L["waiter / actions / page_factory"]
    K --> M["test runs"]
    M --> N{"failed?"}
    N -->|"yes"| O["capture screenshot + page source"]
    N --> P["stop video (per policy)"]
    O --> P
    P --> Q["driver.quit() (clean mode)"]
    Q --> R["report summary flush"]
    R --> S["server stop (if managed)"]
```

---

## Debug logs

`appium-pytest-kit` logs every action, wait, and session lifecycle event using Python's standard `logging` module. Enable them with a single pytest flag:

```bash
pytest --log-cli-level=INFO    # session lifecycle + artifacts
pytest --log-cli-level=DEBUG   # full trace (every tap, wait, scroll)
```

Or persist in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
log_cli       = true
log_cli_level = "INFO"
```

See [docs/troubleshooting.md](docs/troubleshooting.md) for a full table of log messages.

---

## Local development

```bash
pip install -e ".[dev]"
python -m ruff check .
python -m pytest -q
python -m pytest --collect-only examples/basic/tests -q
```

---

## Documentation

| Topic | File |
|---|---|
| Installation + dependencies | [docs/installation.md](docs/installation.md) |
| Project structure + scaffold | [docs/project-structure.md](docs/project-structure.md) |
| Configuration (all settings) | [docs/configuration.md](docs/configuration.md) |
| **CLI reference (all flags)** | [docs/cli-reference.md](docs/cli-reference.md) |
| Built-in fixtures | [docs/fixtures.md](docs/fixtures.md) |
| Page objects guide | [docs/page-objects.md](docs/page-objects.md) |
| conftest.py guide | [docs/conftest-guide.md](docs/conftest-guide.md) |
| Waits reference | [docs/waits.md](docs/waits.md) |
| Actions reference | [docs/actions.md](docs/actions.md) |
| Session modes | [docs/session-modes.md](docs/session-modes.md) |
| Device resolution | [docs/device-resolution.md](docs/device-resolution.md) |
| Failure diagnostics + video | [docs/diagnostics.md](docs/diagnostics.md) |
| Performance checks | [docs/performance.md](docs/performance.md) |
| Error reference | [docs/errors.md](docs/errors.md) |
| Troubleshooting | [docs/troubleshooting.md](docs/troubleshooting.md) |
