# Waits Reference

`Waiter` wraps Selenium's `WebDriverWait` and raises `WaitTimeoutError` (instead of raw `TimeoutException`) on timeout. All methods accept an optional `timeout` parameter that overrides the default.

The default timeout is set by `APP_EXPLICIT_WAIT_TIMEOUT` (default: `10.0` seconds).

---

## Method reference

| Method | Returns | Description |
|---|---|---|
| `for_presence(locator, *, timeout)` | element | Element exists in DOM (may be off-screen) |
| `for_visibility(locator, *, timeout)` | element | Element is visible on screen |
| `for_clickable(locator, *, timeout)` | element | Element is visible and enabled |
| `for_invisibility(locator, *, timeout)` | `bool` | Element is gone or hidden |
| `for_text_contains(locator, text, *, timeout)` | `bool` | Element text contains substring |
| `for_text_equals(locator, text, *, timeout)` | element | Element text exactly matches |
| `for_all_visible(locators, *, timeout)` | `list` | All locators visible simultaneously |
| `for_all_gone(locators, *, timeout)` | `bool` | All locators invisible or absent |
| `for_any_visible(locators, *, timeout)` | element | First visible locator from list |
| `for_context_contains(substring, *, timeout)` | `str` | Driver context name contains substring |
| `for_android_activity(partial_name, *, timeout)` | `str` | Android activity name contains string |
| `until(condition, *, timeout, message)` | any | Custom callable |

All methods raise `WaitTimeoutError` on timeout.

---

## Element presence vs visibility

```python
from appium.webdriver.common.appiumby import AppiumBy

LOCATOR = (AppiumBy.ID, "com.example.app:id/button")

# Presence — element is in the DOM but may be invisible (off-screen, opacity 0)
element = waiter.for_presence(LOCATOR)

# Visibility — element is visible, rendered, not hidden
element = waiter.for_visibility(LOCATOR)
element = waiter.for_visibility(LOCATOR, timeout=20.0)   # custom timeout

# Clickable — visible AND enabled (not disabled)
element = waiter.for_clickable(LOCATOR)
element.click()  # safe to interact immediately

# Invisibility — wait for element to disappear or be hidden
waiter.for_invisibility((AppiumBy.ACCESSIBILITY_ID, "loading_spinner"))
```

---

## Text waits

```python
STATUS = (AppiumBy.ID, "com.example.app:id/status")

# Wait until element text contains the substring "Success"
waiter.for_text_contains(STATUS, "Success")

# Wait until element text is exactly "Upload complete"
element = waiter.for_text_equals(STATUS, "Upload complete")
# for_text_equals returns the element, for_text_contains returns True

# Custom timeout for slow operations
waiter.for_text_contains(STATUS, "Processed", timeout=60.0)
```

---

## Collection waits

```python
HEADER = (AppiumBy.ID, "com.example.app:id/header")
CONTENT = (AppiumBy.ID, "com.example.app:id/content")
FOOTER = (AppiumBy.ID, "com.example.app:id/footer")

# Wait until ALL three are visible at the same time (single timeout for the group)
elements = waiter.for_all_visible([HEADER, CONTENT, FOOTER])
# returns [header_element, content_element, footer_element]

# Wait until ALL three are gone
DIALOG = (AppiumBy.ID, "com.example.app:id/dialog")
OVERLAY = (AppiumBy.ID, "com.example.app:id/overlay")
waiter.for_all_gone([DIALOG, OVERLAY])

# Wait until the FIRST of these becomes visible
ERROR_DIALOG = (AppiumBy.ID, "com.example.app:id/error_dialog")
SUCCESS_DIALOG = (AppiumBy.ID, "com.example.app:id/success_dialog")
visible = waiter.for_any_visible([ERROR_DIALOG, SUCCESS_DIALOG])
# returns whichever element appeared first
```

> **`for_all_visible` timeout note:** The timeout applies to the whole group, not per element. With 5 locators and `timeout=10`, you get one 10-second window for all of them to become visible simultaneously.

---

## Platform / context waits

```python
# Hybrid apps — wait for a WEBVIEW context to become available
ctx_name = waiter.for_context_contains("WEBVIEW")
driver.switch_to.context(ctx_name)

# Wait for a specific WEBVIEW (when there are multiple)
ctx_name = waiter.for_context_contains("WEBVIEW_com.example")

# Android — wait for a specific activity
activity = waiter.for_android_activity("MainActivity")
# returns the full activity name string
waiter.for_android_activity("SettingsActivity", timeout=5.0)
```

---

## Custom conditions

Use `waiter.until()` for any condition Selenium's `expected_conditions` doesn't cover:

```python
from selenium.webdriver.support import expected_conditions as EC

# Standard EC condition with custom timeout
element = waiter.until(
    EC.element_to_be_clickable(locator),
    timeout=5.0,
    message="Submit button never became clickable",
)

# Custom lambda
def _has_items(driver):
    items = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.ListView")
    return len(items) > 0 or False

waiter.until(_has_items, timeout=15.0, message="List never populated")

# Wait for a network call to complete (custom driver attribute)
def _loading_done(driver):
    try:
        spinner = driver.find_element(AppiumBy.ID, "com.example.app:id/progress")
        return not spinner.is_displayed()
    except Exception:
        return True  # spinner gone = loading done

waiter.until(_loading_done, timeout=30.0, message="Loading never finished")
```

---

## `WaitTimeoutError` context

When a wait times out you get a structured error:

```python
from appium_pytest_kit import WaitTimeoutError

try:
    waiter.for_visibility(("id", "missing_btn"), timeout=5.0)
except WaitTimeoutError as exc:
    print(exc.locator)   # ("id", "missing_btn")
    print(exc.timeout)   # 5.0
    print(str(exc))      # includes locator and timeout context
```

Use it in tests to provide a clear skip or failure message:

```python
from appium_pytest_kit import WaitTimeoutError

try:
    waiter.for_visibility(WELCOME_SCREEN, timeout=15.0)
except WaitTimeoutError:
    pytest.fail("Welcome screen never appeared after login")
```

---

## Using `waiter` in page objects

Inside a page class, access the waiter via `self._waiter`:

```python
class LoginPage(BasePage):
    _USERNAME = (AppiumBy.ID, "com.example.app:id/username")

    def wait_until_loaded(self, *, timeout: float = 10.0) -> "LoginPage":
        self._waiter.for_visibility(self._USERNAME, timeout=timeout)
        return self

    def wait_for_error(self) -> str:
        ERROR = (AppiumBy.ID, "com.example.app:id/error_msg")
        element = self._waiter.for_visibility(ERROR, timeout=5.0)
        return element.text
```

---

## The `Waiter` class directly

You can also create a `Waiter` independently of the fixture (useful for utilities or flows):

```python
from appium_pytest_kit import Waiter

waiter = Waiter(driver, default_timeout=15.0, poll_frequency=0.5)
waiter.for_visibility(locator)

# Read the current default timeout
print(waiter.default_timeout)  # 15.0
```
