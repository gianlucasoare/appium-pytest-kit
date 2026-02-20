# conftest.py Guide

`conftest.py` is pytest's mechanism for sharing fixtures, hooks, and helpers across test files. `appium-pytest-kit` uses it as the primary place to extend the framework for your specific project.

---

## How conftest.py works

- pytest automatically loads any `conftest.py` it finds in the directory tree
- Fixtures and hooks in `conftest.py` are available to every test in the same directory and all subdirectories
- You can have **multiple** conftest files at different levels:

```
my-project/
├── conftest.py              ← loaded for all tests
├── tests/
│   ├── conftest.py          ← loaded for tests/ only
│   ├── android/
│   │   ├── conftest.py      ← loaded for tests/android/ only
│   │   └── test_login.py
│   └── ios/
│       ├── conftest.py      ← loaded for tests/ios/ only
│       └── test_login.py
```

Use the root `conftest.py` for project-wide things (hooks, auth fixtures, shared locators). Use sub-level conftest files for platform-specific fixtures.

---

## Minimal `conftest.py`

A basic starting point for any project:

```python
# conftest.py
"""Project-wide test fixtures and hook implementations."""

import pytest
from appium_pytest_kit import AppiumPytestKitSettings
```

Even this empty one is enough. The framework auto-injects all its fixtures — `driver`, `waiter`, `actions`, `page_factory` etc. — without any configuration in conftest.

---

## Extension hooks

The three hooks let you customise the framework without modifying it.

### Hook 1 — Override settings at session start

```python
# conftest.py

def pytest_appium_pytest_kit_configure_settings(settings: AppiumPytestKitSettings):
    """Called once at session start. Return a new settings object to override."""
    # Example: bump the explicit wait timeout for a slow staging environment
    return settings.model_copy(update={"explicit_wait_timeout": 20.0})
```

Return `None` (or omit `return`) to leave settings unchanged.

This hook uses `firstresult=True`, so only the **first non-None return** is used if multiple conftest files implement it.

### Hook 2 — Add capabilities before each driver session

```python
# conftest.py

def pytest_appium_pytest_kit_capabilities(capabilities, settings):
    """Return a dict of extra capabilities to merge before each driver session."""
    extra = {}

    if settings.platform == "android":
        extra["autoGrantPermissions"] = True
        extra["language"] = "en"
        extra["locale"] = "US"

    if settings.platform == "ios":
        extra["wdaLocalPort"] = 8100
        extra["useNewWDA"] = False

    return extra
```

Return `None` to add nothing. All returning implementations are collected and merged.

### Hook 3 — Run code immediately after driver creation

```python
# conftest.py

def pytest_appium_pytest_kit_driver_created(driver, settings):
    """Called right after each Appium session is created."""
    driver.orientation = "PORTRAIT"
    # driver is the raw appium.webdriver.Remote — full API available
```

Return value is ignored. Exceptions propagate and fail the test.

---

## Custom fixtures

### Convenience page fixtures

Define these once so every test just asks for `login_page` or `home_page`:

```python
# conftest.py
import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.profile_page import ProfilePage


@pytest.fixture
def login_page(page_factory):
    return page_factory(LoginPage)


@pytest.fixture
def home_page(page_factory):
    return page_factory(HomePage)


@pytest.fixture
def profile_page(page_factory):
    return page_factory(ProfilePage)
```

### Pre-logged-in fixture

A very common pattern — log in once and hand the test a ready home page:

```python
@pytest.fixture
def logged_in(login_page, home_page):
    """Log in as the default test user, return the home page."""
    login_page.wait_until_loaded()
    login_page.log_in("testuser@example.com", "TestPass1!")
    home_page.wait_until_loaded()
    return home_page
```

Tests that need an authenticated session just use `logged_in`:

```python
def test_home_greeting(logged_in):
    assert logged_in.greeting_text() == "Hello, testuser"
```

### Parametrised credentials

```python
# conftest.py
import pytest

@pytest.fixture(params=[
    ("admin@example.com",  "AdminPass1!"),
    ("viewer@example.com", "ViewerPass1!"),
])
def user_credentials(request):
    return request.param


@pytest.fixture
def logged_in_as(user_credentials, login_page, home_page):
    email, password = user_credentials
    login_page.log_in(email, password)
    home_page.wait_until_loaded()
    return home_page
```

```python
def test_all_users_can_see_home(logged_in_as):
    assert logged_in_as.is_loaded()
    # runs twice — once per user
```

### Platform-conditional fixture

```python
@pytest.fixture
def skip_on_ios(settings):
    """Skip this test automatically when running on iOS."""
    if settings.platform == "ios":
        pytest.skip("Not applicable on iOS")

@pytest.fixture
def skip_on_android(settings):
    if settings.platform == "android":
        pytest.skip("Not applicable on Android")
```

Usage:

```python
def test_android_back_button(skip_on_ios, actions):
    actions.press_keycode(4)  # Android BACK key
```

### Dismiss optional onboarding

Many apps show a one-time onboarding or permissions dialog on first launch. Handle it for all tests:

```python
@pytest.fixture(autouse=True)
def dismiss_onboarding(actions):
    """Dismiss one-time onboarding dialogs before each test, if present."""
    SKIP_BTN = (AppiumBy.ACCESSIBILITY_ID, "Skip")
    ALLOW_BTN = (AppiumBy.ACCESSIBILITY_ID, "Allow")
    actions.tap_if_present(SKIP_BTN, timeout=2.0)
    actions.tap_if_present(ALLOW_BTN, timeout=2.0)
    # autouse=True means this runs before every test automatically
```

---

## Shared constants and locators

For a small project, locators that are shared across many tests can live in conftest:

```python
# conftest.py
from appium.webdriver.common.appiumby import AppiumBy
from appium_pytest_kit import Locator

# Shared navigation locators
NAV_HOME: Locator = (AppiumBy.ACCESSIBILITY_ID, "nav_home")
NAV_BACK: Locator = (AppiumBy.ACCESSIBILITY_ID, "nav_back")
LOADING_SPINNER: Locator = (AppiumBy.ID, "com.example.app:id/progress")
```

For a larger project, put locators in the page class itself — see [Page objects guide →](page-objects.md).

---

## Complete `conftest.py` example

A realistic conftest.py for a medium-sized project:

```python
# conftest.py
"""Project-wide fixtures and hook implementations for my-app tests."""

import pytest
from appium.webdriver.common.appiumby import AppiumBy

from appium_pytest_kit import AppiumPytestKitSettings, Locator
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.profile_page import ProfilePage


# ── Framework hooks ────────────────────────────────────────────────────────────


def pytest_appium_pytest_kit_configure_settings(settings: AppiumPytestKitSettings):
    """Increase wait timeout for the staging environment."""
    if "staging" in (settings.appium_url or ""):
        return settings.model_copy(update={"explicit_wait_timeout": 20.0})


def pytest_appium_pytest_kit_capabilities(capabilities, settings):
    """Add platform-specific extra capabilities."""
    if settings.platform == "android":
        return {"autoGrantPermissions": True, "language": "en", "locale": "US"}
    if settings.platform == "ios":
        return {"wdaLocalPort": 8100}


def pytest_appium_pytest_kit_driver_created(driver, settings):
    """Lock orientation to portrait for all tests."""
    try:
        driver.orientation = "PORTRAIT"
    except Exception:
        pass  # non-fatal — some devices don't support orientation lock


# ── Shared page fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def login_page(page_factory):
    return page_factory(LoginPage)


@pytest.fixture
def home_page(page_factory):
    return page_factory(HomePage)


@pytest.fixture
def profile_page(page_factory):
    return page_factory(ProfilePage)


# ── Auth flow fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def logged_in(login_page, home_page):
    """Log in as the default test user and return the home page."""
    login_page.wait_until_loaded()
    login_page.log_in("testuser@example.com", "TestPass1!")
    home_page.wait_until_loaded()
    return home_page


# ── Platform helper fixtures ───────────────────────────────────────────────────


@pytest.fixture
def skip_on_ios(settings):
    if settings.platform == "ios":
        pytest.skip("Android-only test")


@pytest.fixture
def skip_on_android(settings):
    if settings.platform == "android":
        pytest.skip("iOS-only test")


# ── Common auto-dismiss ────────────────────────────────────────────────────────


_DISMISS_LOCATORS: list[Locator] = [
    (AppiumBy.ACCESSIBILITY_ID, "Skip"),
    (AppiumBy.ACCESSIBILITY_ID, "Allow"),
    (AppiumBy.ACCESSIBILITY_ID, "OK"),
    (AppiumBy.ACCESSIBILITY_ID, "Got it"),
]


@pytest.fixture(autouse=True)
def dismiss_optional_dialogs(actions):
    """Dismiss common one-time dialogs before each test."""
    for locator in _DISMISS_LOCATORS:
        actions.tap_if_present(locator, timeout=1.0)
```

---

## Sub-level conftest for Android vs iOS

When you have different setups per platform:

```python
# tests/android/conftest.py
"""Android-specific fixtures."""
import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_android(settings):
    if settings.platform != "android":
        pytest.skip("Android-only test suite")
```

```python
# tests/ios/conftest.py
"""iOS-specific fixtures."""
import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_ios(settings):
    if settings.platform != "ios":
        pytest.skip("iOS-only test suite")
```

---

## Next steps

- [Session modes →](session-modes.md) — controlling driver lifecycle
- [Page objects guide →](page-objects.md) — building page classes
- [Fixtures reference →](fixtures.md) — all built-in fixtures explained
