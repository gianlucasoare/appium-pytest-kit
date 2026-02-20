# Built-in Fixtures

All fixtures are provided automatically by the plugin — no imports or configuration required in test files. Just add the fixture name as a function argument and it works.

---

## Fixture overview

| Fixture | Scope | Description |
|---|---|---|
| `settings` | session | Resolved `AppiumPytestKitSettings` |
| `device_info` | session | Resolved `DeviceInfo` (device name, UDID, version) |
| `appium_server` | session | `AppiumServerInfo` — URL and whether it is managed |
| `driver` | function | Live `appium.webdriver.Remote` instance |
| `waiter` | function | `Waiter` bound to current driver |
| `actions` | function | `MobileActions` bound to driver and waiter |
| `page_factory` | function | Factory for creating page objects without boilerplate |

---

## `settings` — session scope

The resolved `AppiumPytestKitSettings` instance. Loaded once for the whole session and available everywhere.

```python
def test_platform_is_configured(settings):
    assert settings.platform in {"android", "ios"}

def test_appium_url_uses_default(settings):
    assert settings.appium_url == "http://127.0.0.1:4723"

def test_all_fields_accessible(settings):
    print(settings.app_package)
    print(settings.device_name)
    print(settings.session_mode)
    print(settings.explicit_wait_timeout)
```

Use `settings` in conftest.py to conditionally configure your app:

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def platform(settings):
    return settings.platform

@pytest.fixture(scope="session")
def is_android(settings):
    return settings.platform == "android"
```

---

## `device_info` — session scope

Returns the resolved `DeviceInfo` from the 3-tier device resolver (explicit settings → yaml profile → auto-detect). Returns `None` if no device is configured.

```python
def test_device_was_resolved(device_info):
    assert device_info is not None
    print(device_info.device_name)     # "Pixel 7"
    print(device_info.udid)            # "emulator-5554"
    print(device_info.platform_name)   # "android"
    print(device_info.platform_version) # "14"
    print(device_info.is_simulator)    # False
```

Fields on `DeviceInfo`:

| Field | Type | Description |
|---|---|---|
| `device_name` | `str` | Human-readable device name |
| `platform_name` | `str` | `"android"` or `"ios"` |
| `udid` | `str\|None` | Unique device identifier |
| `platform_version` | `str\|None` | OS version string |
| `automation_name` | `str\|None` | Automation driver name |
| `is_simulator` | `bool` | `True` for iOS simulators |

---

## `appium_server` — session scope

Provides information about the resolved Appium server. If `APP_MANAGE_APPIUM_SERVER=true`, the framework starts a local Appium process and yields after it's ready; it is stopped at session end.

```python
def test_server_is_reachable(appium_server):
    assert appium_server.url.startswith("http")
    assert isinstance(appium_server.managed, bool)
```

Fields on `AppiumServerInfo`:

| Field | Type | Description |
|---|---|---|
| `url` | `str` | Full URL of the Appium server |
| `managed` | `bool` | `True` when the framework started the server |

---

## `driver` — function scope

A live `appium.webdriver.Remote` instance. Created before each test, quit automatically after — even if the test raises an exception.

```python
import pytest
from appium.webdriver.common.appiumby import AppiumBy

@pytest.mark.integration
def test_app_launches(driver):
    assert driver.session_id is not None

@pytest.mark.integration
def test_driver_has_full_api(driver):
    # Use the full Appium/Selenium API directly
    els = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
    assert len(els) > 0

@pytest.mark.integration
def test_page_source_is_available(driver):
    source = driver.page_source
    assert "<hierarchy" in source or "<?xml" in source
```

The driver's lifetime depends on `APP_SESSION_MODE`:
- `clean` — new driver per test (default)
- `clean-session` — one shared driver for the whole session
- `debug` — shared driver, kept alive after failures

See [Session modes →](session-modes.md) for details.

---

## `waiter` — function scope

A `Waiter` instance bound to the current `driver`. Provides explicit waits that raise `WaitTimeoutError` instead of raw Selenium exceptions.

The default timeout is controlled by `APP_EXPLICIT_WAIT_TIMEOUT` (default: `10.0` seconds).

```python
from appium.webdriver.common.appiumby import AppiumBy

@pytest.mark.integration
def test_wait_for_element(waiter):
    locator = (AppiumBy.ID, "com.example.app:id/title")

    # Wait up to 10 s (default) for presence
    element = waiter.for_presence(locator)

    # Wait up to 10 s for visibility
    element = waiter.for_visibility(locator)

    # Custom timeout
    element = waiter.for_visibility(locator, timeout=20.0)

    # Wait for text
    waiter.for_text_contains(locator, "Welcome")

    # Custom condition
    from selenium.webdriver.support import expected_conditions as EC
    element = waiter.until(EC.element_to_be_clickable(locator), timeout=5.0)
```

All waiter methods — see [Waits reference →](waits.md).

---

## `actions` — function scope

A `MobileActions` instance with high-level interaction helpers. Uses `waiter` under the hood.

```python
from appium.webdriver.common.appiumby import AppiumBy

USERNAME = (AppiumBy.ID, "com.example.app:id/username")
PASSWORD = (AppiumBy.ID, "com.example.app:id/password")
LOGIN_BTN = (AppiumBy.ID, "com.example.app:id/login_button")
WELCOME = (AppiumBy.ID, "com.example.app:id/welcome_text")

@pytest.mark.integration
def test_login_flow(actions):
    actions.type_text(USERNAME, "testuser")
    actions.type_text(PASSWORD, "secret")
    actions.tap(LOGIN_BTN)
    assert actions.text(WELCOME) == "Welcome, testuser"
```

All actions methods — see [Actions reference →](actions.md).

---

## `page_factory` — function scope

A factory fixture for creating page objects without repeating the `(driver, waiter, actions)` triplet every time.

```python
# Without page_factory — verbose
def test_login(driver, waiter, actions):
    login = LoginPage(driver, waiter, actions)
    home = HomePage(driver, waiter, actions)
    login.enter_credentials("user", "pass")
    login.submit()
    assert home.is_loaded()

# With page_factory — clean
def test_login(page_factory):
    login = page_factory(LoginPage)
    home = page_factory(HomePage)
    login.enter_credentials("user", "pass")
    login.submit()
    assert home.is_loaded()
```

`page_factory` calls `PageClass(driver, waiter, actions)` — so your page's `__init__` must accept exactly those three arguments. `BasePage` handles this for you automatically.

See [Page objects guide →](page-objects.md) for full examples.

---

## Writing your own fixtures

You can write custom fixtures in `conftest.py` that depend on any built-in fixture:

```python
# conftest.py
import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage


@pytest.fixture
def login_page(page_factory):
    """Ready-to-use LoginPage for any test that needs it."""
    return page_factory(LoginPage)


@pytest.fixture
def home_page(page_factory):
    return page_factory(HomePage)


@pytest.fixture
def logged_in_user(login_page, home_page):
    """Log in as the default test user and return the home page."""
    login_page.enter_credentials("testuser", "testpass")
    login_page.submit()
    home_page.wait_until_loaded()
    return home_page
```

Tests then just ask for `logged_in_user`:

```python
def test_home_greeting(logged_in_user):
    assert logged_in_user.greeting_text() == "Hello, testuser"

def test_home_has_menu(logged_in_user):
    assert logged_in_user.menu_is_visible()
```

See [conftest guide →](conftest-guide.md) for more patterns.

---

## Fixture lifecycle diagram

```
pytest session start
    │
    ├── settings (session)       ← load .env + env vars + CLI overrides
    ├── device_info (session)    ← resolve device (3-tier)
    └── appium_server (session)  ← start or connect to Appium server
          │
          ╔ per test ════════════════════════════════════════════════════╗
          ║ driver (function)    ← create Appium session                ║
          ║ waiter (function)    ← bound to driver                      ║
          ║ actions (function)   ← bound to driver + waiter             ║
          ║ page_factory (func)  ← factory using driver, waiter, actions║
          ║                                                             ║
          ║    test runs                                                ║
          ║                                                             ║
          ║ [on failure] capture screenshot + page source + device logs ║
          ║ [on failure/always] save video recording                    ║
          ║ driver.quit()                                               ║
          ╚═════════════════════════════════════════════════════════════╝
          │
    appium_server: stop managed server (if managed)
    reporter: write summary.json (if reporting enabled)
```
