# Page Objects

The Page Object pattern keeps your tests readable and maintainable. Each page (or screen) in your app gets a Python class that:
- Defines its own locators as private class attributes
- Exposes meaningful methods like `enter_credentials()` instead of raw `tap()` calls
- Hides Appium internals from the test

---

## The `Locator` type

A locator is a `tuple[str, str]` — a strategy and a value:

```python
from appium.webdriver.common.appiumby import AppiumBy
from appium_pytest_kit import Locator

# These are all Locator values
USERNAME_FIELD: Locator = (AppiumBy.ID, "com.example.app:id/username")
TITLE: Locator = (AppiumBy.ACCESSIBILITY_ID, "main_title")
SUBMIT_BTN: Locator = (AppiumBy.XPATH, "//android.widget.Button[@text='Submit']")
```

`Locator` is exported from the top-level package so you can use it for type annotations anywhere:

```python
from appium_pytest_kit import Locator
```

---

## `BasePage` — the foundation

The scaffold generates a `pages/base_page.py` that every page inherits:

```python
# pages/base_page.py
from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.waits import Waiter


class BasePage:
    """Composition base — gives every page access to driver, waiter, and actions."""

    def __init__(self, driver, waiter: Waiter, actions: MobileActions) -> None:
        self._driver = driver
        self._waiter = waiter
        self._actions = actions
```

`BasePage` intentionally stays thin. It gives subclasses access to the three core objects:
- `self._driver` — the raw Appium `webdriver.Remote` (use when you need the full API)
- `self._waiter` — explicit waits with `WaitTimeoutError` on timeout
- `self._actions` — high-level tap / type / text / scroll helpers

---

## Creating a page: step by step

### Step 1 — Create the file

```
pages/
├── __init__.py
├── base_page.py
├── login_page.py    ← new file
└── home_page.py
```

### Step 2 — Define locators at the top of the class

Keep locators private and grouped at the top. Prefix with `_` to mark them as internal:

```python
# pages/login_page.py
from appium.webdriver.common.appiumby import AppiumBy
from appium_pytest_kit import Locator
from pages.base_page import BasePage

BY_ID = AppiumBy.RESOURCE_ID
BY_AID = AppiumBy.ACCESSIBILITY_ID


class LoginPage(BasePage):
    # ── locators ──────────────────────────────────────────────────────────
    _USERNAME: Locator = (BY_ID, "com.example.app:id/username")
    _PASSWORD: Locator = (BY_ID, "com.example.app:id/password")
    _LOGIN_BTN: Locator = (BY_AID, "login_button")
    _ERROR_MSG: Locator = (BY_ID, "com.example.app:id/error_message")
    _FORGOT_PWD: Locator = (BY_AID, "forgot_password_link")
```

### Step 3 — Add a `is_loaded` or `wait_until_loaded` method

Every page should have a way to confirm it has appeared:

```python
    def is_loaded(self, *, timeout: float = 10.0) -> bool:
        """Return True when the login screen is visible."""
        return self._actions.is_displayed(self._USERNAME, timeout=timeout)

    def wait_until_loaded(self, *, timeout: float = 10.0) -> "LoginPage":
        """Wait for the login screen and return self for chaining."""
        self._waiter.for_visibility(self._USERNAME, timeout=timeout)
        return self
```

### Step 4 — Add interaction methods

Name methods after what the user does, not what the code does:

```python
    def enter_username(self, value: str) -> None:
        self._actions.type_text(self._USERNAME, value)

    def enter_password(self, value: str) -> None:
        self._actions.type_text(self._PASSWORD, value)

    def tap_login(self) -> None:
        self._actions.tap(self._LOGIN_BTN)

    def tap_forgot_password(self) -> None:
        self._actions.tap(self._FORGOT_PWD)
```

### Step 5 — Combine into higher-level flows

```python
    def log_in(self, username: str, password: str) -> None:
        """Fill in credentials and tap the login button."""
        self.enter_username(username)
        self.enter_password(password)
        self.tap_login()
```

### Step 6 — Add read / assertion methods

```python
    def error_message(self) -> str:
        """Return the text of the validation error, if any."""
        return self._actions.text(self._ERROR_MSG)

    def is_error_displayed(self) -> bool:
        return self._actions.is_displayed(self._ERROR_MSG, timeout=2.0)
```

---

## Full `LoginPage` example

```python
# pages/login_page.py
from appium.webdriver.common.appiumby import AppiumBy

from appium_pytest_kit import Locator
from pages.base_page import BasePage

BY_ID = AppiumBy.RESOURCE_ID
BY_AID = AppiumBy.ACCESSIBILITY_ID


class LoginPage(BasePage):
    # ── locators ──────────────────────────────────────────────────────────
    _USERNAME: Locator = (BY_ID, "com.example.app:id/username")
    _PASSWORD: Locator = (BY_ID, "com.example.app:id/password")
    _LOGIN_BTN: Locator = (BY_AID, "login_button")
    _ERROR_MSG: Locator = (BY_ID, "com.example.app:id/error_message")
    _FORGOT_PWD: Locator = (BY_AID, "forgot_password_link")

    # ── load check ────────────────────────────────────────────────────────

    def is_loaded(self, *, timeout: float = 10.0) -> bool:
        return self._actions.is_displayed(self._USERNAME, timeout=timeout)

    def wait_until_loaded(self, *, timeout: float = 10.0) -> "LoginPage":
        self._waiter.for_visibility(self._USERNAME, timeout=timeout)
        return self

    # ── interactions ──────────────────────────────────────────────────────

    def enter_username(self, value: str) -> None:
        self._actions.type_text(self._USERNAME, value)

    def enter_password(self, value: str) -> None:
        self._actions.type_text(self._PASSWORD, value)

    def tap_login(self) -> None:
        self._actions.tap(self._LOGIN_BTN)

    def tap_forgot_password(self) -> None:
        self._actions.tap(self._FORGOT_PWD)

    def log_in(self, username: str, password: str) -> None:
        """Fill in credentials and submit the form."""
        self.enter_username(username)
        self.enter_password(password)
        self.tap_login()

    # ── read / assert ─────────────────────────────────────────────────────

    def error_message(self) -> str:
        return self._actions.text(self._ERROR_MSG)

    def is_error_displayed(self) -> bool:
        return self._actions.is_displayed(self._ERROR_MSG, timeout=2.0)

    def assert_error_contains(self, text: str) -> None:
        self._waiter.for_text_contains(self._ERROR_MSG, text)
```

---

## Full `HomePage` example

```python
# pages/home_page.py
from appium.webdriver.common.appiumby import AppiumBy

from appium_pytest_kit import Locator
from pages.base_page import BasePage

BY_ID = AppiumBy.RESOURCE_ID
BY_AID = AppiumBy.ACCESSIBILITY_ID


class HomePage(BasePage):
    # ── locators ──────────────────────────────────────────────────────────
    _GREETING: Locator = (BY_ID, "com.example.app:id/greeting")
    _NAV_HOME: Locator = (BY_AID, "nav_home")
    _NAV_PROFILE: Locator = (BY_AID, "nav_profile")
    _NAV_SETTINGS: Locator = (BY_AID, "nav_settings")
    _SEARCH_INPUT: Locator = (BY_ID, "com.example.app:id/search")

    # ── load check ────────────────────────────────────────────────────────

    def is_loaded(self, *, timeout: float = 10.0) -> bool:
        return self._actions.is_displayed(self._GREETING, timeout=timeout)

    def wait_until_loaded(self, *, timeout: float = 10.0) -> "HomePage":
        self._waiter.for_visibility(self._GREETING, timeout=timeout)
        return self

    # ── interactions ──────────────────────────────────────────────────────

    def tap_profile(self) -> None:
        self._actions.tap(self._NAV_PROFILE)

    def tap_settings(self) -> None:
        self._actions.tap(self._NAV_SETTINGS)

    def search(self, query: str) -> None:
        self._actions.tap(self._SEARCH_INPUT)
        self._actions.type_text(self._SEARCH_INPUT, query)
        self._actions.press_keycode(66)  # ENTER

    # ── read / assert ─────────────────────────────────────────────────────

    def greeting_text(self) -> str:
        return self._actions.text(self._GREETING)

    def assert_greeting(self, expected: str) -> None:
        self._waiter.for_text_equals(self._GREETING, expected)

    def nav_bar_is_visible(self) -> bool:
        return self._actions.is_displayed_first_available(
            [self._NAV_HOME, self._NAV_PROFILE, self._NAV_SETTINGS]
        )
```

---

## Using pages in tests

### Option A — `page_factory` fixture (recommended)

```python
# tests/test_login.py
import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage


@pytest.mark.integration
def test_successful_login(page_factory):
    login = page_factory(LoginPage)
    home = page_factory(HomePage)

    login.wait_until_loaded()
    login.log_in("testuser", "secret123")
    home.wait_until_loaded()

    assert home.greeting_text() == "Hello, testuser"


@pytest.mark.integration
def test_wrong_password_shows_error(page_factory):
    login = page_factory(LoginPage)

    login.wait_until_loaded()
    login.log_in("testuser", "wrongpassword")

    assert login.is_error_displayed()
    assert "Invalid" in login.error_message()
```

### Option B — individual fixtures in conftest

Define convenience fixtures once in `conftest.py`:

```python
# conftest.py
import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage


@pytest.fixture
def login_page(page_factory):
    return page_factory(LoginPage)


@pytest.fixture
def home_page(page_factory):
    return page_factory(HomePage)


@pytest.fixture
def logged_in(login_page, home_page):
    """Log in as default user, return home page."""
    login_page.log_in("testuser", "secret123")
    home_page.wait_until_loaded()
    return home_page
```

Tests become very clean:

```python
def test_home_loads_after_login(logged_in):
    assert logged_in.is_loaded()

def test_greeting_after_login(logged_in):
    assert logged_in.greeting_text() == "Hello, testuser"
```

---

## Tips for organising pages

1. **One file per screen.** Don't put multiple pages in one file.

2. **Keep locators private.** Prefix with `_` and define them at the top of the class. Tests should never reference locators directly.

3. **Name methods from the user's perspective.** `log_in()` not `click_login_button()`. `error_message()` not `get_error_text_element_text()`.

4. **Return `self` for fluent chaining** (optional):
   ```python
   login.wait_until_loaded().log_in("user", "pass")
   ```

5. **Use `_waiter.for_visibility` for load checks**, not `time.sleep`. Your tests will be faster and more reliable.

6. **Platform-specific pages** — use a naming convention or subclass:
   ```python
   # pages/android/home_page.py
   # pages/ios/home_page.py
   ```
   Then in conftest.py, create the right page based on `settings.platform`.

7. **Don't put assertions in pages.** Keep pages as action/query objects. Put assertions in tests or flow objects.

---

## Next steps

- [conftest guide →](conftest-guide.md) — creating fixtures and wiring everything together
- [Actions reference →](actions.md) — all available `MobileActions` methods
- [Waits reference →](waits.md) — all available `Waiter` methods
