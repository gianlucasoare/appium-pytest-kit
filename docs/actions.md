# Actions Reference

`MobileActions` provides high-level UI interaction helpers built on top of `Waiter`. All methods wait for the target element to be visible before interacting — no need to add explicit waits before every tap or type call.

All methods raise `ActionError` on failure (wrapping the underlying `WebDriverException`).

---

## Tap / gesture

### `tap(locator, *, timeout=10.0)`

Tap a visible element. Waits for visibility first.

```python
SUBMIT_BTN = (AppiumBy.ACCESSIBILITY_ID, "submit_button")

actions.tap(SUBMIT_BTN)
actions.tap(SUBMIT_BTN, timeout=20.0)   # wait longer for slow transitions
```

### `tap_if_present(locator, *, timeout=2.0) → bool`

Tap the element if visible within `timeout`. Returns `True` if tapped, `False` if not found. Never raises.

```python
# Dismiss optional cookie banner or onboarding screen
SKIP_BTN = (AppiumBy.ACCESSIBILITY_ID, "Skip")
tapped = actions.tap_if_present(SKIP_BTN, timeout=3.0)
if not tapped:
    print("Skip button was not present — continuing")
```

### `tap_if_present_first_available(locators, *, timeout=2.0) → bool`

Tap the first locator from the list that is visible. Returns `True` if any was tapped.

```python
# Accept button has different IDs across app versions
actions.tap_if_present_first_available([
    (AppiumBy.ID, "btn_accept_v1"),
    (AppiumBy.ID, "btn_accept_v2"),
    (AppiumBy.ACCESSIBILITY_ID, "Accept"),
])
```

### `tap_by_coordinates(x, y)`

Tap at absolute screen pixel coordinates. Useful when elements have no reliable locator.

```python
actions.tap_by_coordinates(200, 450)
```

### `tap_center(locator, *, timeout=10.0)`

Tap the visual center of an element (useful for elements where `.click()` misses).

```python
MAP_ICON = (AppiumBy.ACCESSIBILITY_ID, "map_pin")
actions.tap_center(MAP_ICON)
```

### `double_tap(locator, *, timeout=10.0)`

Two quick taps (for zoom or item selection in some UIs).

```python
IMAGE = (AppiumBy.ID, "com.example.app:id/photo")
actions.double_tap(IMAGE)
```

### `long_press(locator, *, duration_seconds=2.0, timeout=10.0)`

Hold-press gesture for context menus or drag handles.

```python
LIST_ITEM = (AppiumBy.ID, "com.example.app:id/list_item")
actions.long_press(LIST_ITEM, duration_seconds=1.5)
```

---

## Text input

### `type_text(locator, value, *, clear_first=True, timeout=10.0)`

Wait for the field, optionally clear it, then type. This is the standard method for text input.

```python
USERNAME = (AppiumBy.ID, "com.example.app:id/username")

actions.type_text(USERNAME, "testuser")
actions.type_text(USERNAME, "updated", clear_first=True)   # default: clear first
actions.type_text(USERNAME, " append", clear_first=False)  # append without clearing
```

### `type_if_present(locator, value, *, clear_first=True, timeout=3.0) → bool`

Type into the field if it's visible within `timeout`. Returns `True` if typed.

```python
SEARCH = (AppiumBy.ID, "com.example.app:id/search")
typed = actions.type_if_present(SEARCH, "query", timeout=2.0)
```

### `type_if_present_first_available(locators, value, *, clear_first=True, timeout=3.0) → bool`

Type into the first visible field from the list.

```python
# Email and phone number fields have different IDs
actions.type_if_present_first_available([
    (AppiumBy.ID, "email_field"),
    (AppiumBy.ID, "phone_field"),
], "user@example.com")
```

### `type_first_available(locators, value, *, clear_first=True, timeout=10.0) → bool`

Like `type_if_present_first_available` but with a longer timeout (use when the field may take time to appear).

### `type_text_slowly(locator, value, *, delay_per_char=0.1, clear_first=True, timeout=10.0)`

Type character-by-character with a delay. Use this when the app drops characters under fast input (common with OTP or autocomplete fields).

```python
OTP_FIELD = (AppiumBy.ID, "com.example.app:id/otp")
actions.type_text_slowly(OTP_FIELD, "123456", delay_per_char=0.15)
```

### `clear(locator, *, timeout=10.0)`

Clear the text content of a field without typing anything.

```python
SEARCH = (AppiumBy.ID, "com.example.app:id/search")
actions.clear(SEARCH)
```

---

## Assertions

### `is_displayed(locator, *, timeout=None) → bool`

Returns `True` if the element is visible within `timeout` (defaults to `waiter.default_timeout`). Never raises.

```python
WELCOME = (AppiumBy.ID, "com.example.app:id/welcome")

if actions.is_displayed(WELCOME):
    print("Welcome screen is showing")

# Quick check with a short timeout
if actions.is_displayed(WELCOME, timeout=1.0):
    print("Appeared quickly")
```

### `assert_displayed(locator, *, timeout=None)`

Raises `AssertionError` if the element is not visible within `timeout`.

```python
HOME_TITLE = (AppiumBy.ID, "com.example.app:id/home_title")
actions.assert_displayed(HOME_TITLE)                    # uses default_timeout
actions.assert_displayed(HOME_TITLE, timeout=15.0)      # custom timeout
```

### `is_displayed_first_available(locators, *, timeout=None) → bool`

Returns `True` if **any** locator from the list is visible.

```python
CONFIRM_BTNS = [
    (AppiumBy.ACCESSIBILITY_ID, "OK"),
    (AppiumBy.ACCESSIBILITY_ID, "Confirm"),
    (AppiumBy.ACCESSIBILITY_ID, "Yes"),
]
if actions.is_displayed_first_available(CONFIRM_BTNS, timeout=2.0):
    actions.tap_if_present_first_available(CONFIRM_BTNS)
```

### `assert_displayed_first_available(locators, *, timeout=None)`

Raises `AssertionError` if **none** of the locators are visible.

```python
actions.assert_displayed_first_available([
    (AppiumBy.ID, "success_banner"),
    (AppiumBy.ID, "success_toast"),
], timeout=10.0)
```

### `not_displayed_first_available(locators, *, timeout=None) → bool`

Returns `True` if **none** of the locators are visible (inverse of `is_displayed_first_available`).

```python
LOADING_INDICATORS = [
    (AppiumBy.ID, "spinner"),
    (AppiumBy.ID, "progress_bar"),
]
# Poll until loading finishes
waiter.until(
    lambda d: actions.not_displayed_first_available(LOADING_INDICATORS, timeout=0.5)
)
```

### `assert_not_displayed_first_available(locators, *, timeout=None)`

Raises `AssertionError` if **any** of the locators is visible.

```python
ERRORS = [
    (AppiumBy.ID, "error_banner"),
    (AppiumBy.ID, "error_toast"),
]
actions.assert_not_displayed_first_available(ERRORS, timeout=2.0)
```

### `is_not_displayed(locator, *, timeout=None) → bool`

Returns `True` if the element is **not** visible within `timeout` (the element may be hidden or absent from the DOM). The logical inverse of `is_displayed`.

```python
LOADING = (AppiumBy.ID, "com.example.app:id/spinner")

# Wait for spinner to disappear
waiter.for_invisibility(LOADING)

# Or check in a conditional
if actions.is_not_displayed(LOADING, timeout=5.0):
    print("Loading finished")
```

### `assert_not_displayed(locator, *, timeout=None)`

Raises `AssertionError` if the element is **still visible** after `timeout`.

```python
ERROR_TOAST = (AppiumBy.ID, "com.example.app:id/error_toast")
actions.tap(DISMISS_BTN)
actions.assert_not_displayed(ERROR_TOAST, timeout=3.0)
```

> **`is_displayed` vs `exists`**
> - `is_displayed` — element must be rendered and visible on screen
> - `exists` — element just needs to be in the DOM (may be off-screen or hidden)

---

## Text assertions

### `assert_text(locator, expected, *, timeout=None)`

Assert that the element's text **exactly equals** `expected`. Raises `AssertionError` with a clear diff showing expected vs actual.

```python
TOTAL = (AppiumBy.ID, "com.example.app:id/order_total")
actions.assert_text(TOTAL, "$12.99")
```

### `assert_text_contains(locator, partial, *, timeout=None)`

Assert that the element's text **contains** `partial` as a substring.

```python
GREETING = (AppiumBy.ID, "com.example.app:id/greeting")
actions.assert_text_contains(GREETING, "testuser")   # "Welcome, testuser!" passes
```

### `assert_text_not_empty(locator, *, timeout=None)`

Assert that the element's text is not blank (empty string or whitespace only).

```python
RESULT = (AppiumBy.ID, "com.example.app:id/result_label")
actions.assert_text_not_empty(RESULT)
```

---

## Attribute assertion

### `assert_attribute(locator, attr, expected, *, timeout=None)`

Assert that the element attribute `attr` equals `expected`. Use when you need to verify a specific attribute value rather than just reading it.

```python
TOGGLE = (AppiumBy.ACCESSIBILITY_ID, "dark_mode_toggle")
actions.assert_attribute(TOGGLE, "checked", "true")

FIELD = (AppiumBy.ID, "com.example.app:id/search")
actions.assert_attribute(FIELD, "hint", "Search products")
```

---

## Enabled / disabled state

### `is_enabled(locator, *, timeout=None) → bool`

Returns `True` if the element is visible **and** enabled (interactable). Returns `False` if the element is not found or is disabled.

```python
SUBMIT_BTN = (AppiumBy.ACCESSIBILITY_ID, "submit_button")

if actions.is_enabled(SUBMIT_BTN):
    actions.tap(SUBMIT_BTN)
else:
    print("Submit is disabled — form may be incomplete")
```

### `assert_enabled(locator, *, timeout=None)`

Assert that the element is enabled. Raises `AssertionError` if it is disabled or not found.

```python
SUBMIT_BTN = (AppiumBy.ACCESSIBILITY_ID, "submit_button")
actions.type_text(USERNAME, "user@example.com")
actions.type_text(PASSWORD, "password123")
actions.assert_enabled(SUBMIT_BTN)   # confirm form activated the button
```

### `assert_not_enabled(locator, *, timeout=None)`

Assert that the element is disabled. Raises `AssertionError` if it is enabled. Elements that are not visible are treated as not enabled (assertion passes).

```python
CHECKOUT_BTN = (AppiumBy.ACCESSIBILITY_ID, "checkout_button")
# Cart is empty — checkout should be disabled
actions.assert_not_enabled(CHECKOUT_BTN)
```

---

## Checked / selected state

Use these for checkboxes, toggles, radio buttons, and switches. Checks both `checked` and `selected` attributes to cover Android and iOS elements.

### `is_checked(locator, *, timeout=None) → bool`

Returns `True` if the element is checked or selected.

```python
REMEMBER_ME = (AppiumBy.ACCESSIBILITY_ID, "remember_me_checkbox")

if actions.is_checked(REMEMBER_ME):
    print("Remember Me is on")
```

### `assert_checked(locator, *, timeout=None)`

Assert that the element is checked/selected. Raises `AssertionError` if not.

```python
TERMS_CHECKBOX = (AppiumBy.ID, "com.example.app:id/terms_checkbox")
actions.tap(TERMS_CHECKBOX)
actions.assert_checked(TERMS_CHECKBOX)
```

### `assert_not_checked(locator, *, timeout=None)`

Assert that the element is unchecked/unselected. Raises `AssertionError` if checked.

```python
NOTIFICATIONS_TOGGLE = (AppiumBy.ACCESSIBILITY_ID, "notifications_toggle")
actions.tap(NOTIFICATIONS_TOGGLE)          # toggle off
actions.assert_not_checked(NOTIFICATIONS_TOGGLE)
```

---

## Element count

### `count(locator) → int`

Return the number of elements currently matching `locator` in the DOM. No waiting — reflects the current state at call time.

```python
LIST_ITEM = (AppiumBy.ID, "com.example.app:id/cart_item")
n = actions.count(LIST_ITEM)
print(f"Cart has {n} item(s)")
```

### `assert_count(locator, expected)`

Assert that exactly `expected` elements match `locator`. Raises `AssertionError` with the actual count if they differ.

```python
LIST_ITEM = (AppiumBy.ID, "com.example.app:id/cart_item")

# After adding 3 items to cart
actions.assert_count(LIST_ITEM, 3)

# After clearing the cart
actions.tap(CLEAR_CART_BTN)
actions.assert_count(LIST_ITEM, 0)
```

---

## Read / inspect

### `text(locator, *, timeout=10.0) → str`

Read text from a visible element.

```python
RESULT = (AppiumBy.ID, "com.example.app:id/result")
value = actions.text(RESULT)
assert value == "42"
```

### `attribute(locator, attr, *, timeout=10.0) → str | None`

Read an attribute from a visible element.

```python
SEARCH_FIELD = (AppiumBy.ID, "com.example.app:id/search")

hint = actions.attribute(SEARCH_FIELD, "hint")          # Android placeholder
label = actions.attribute(SEARCH_FIELD, "content-desc") # Accessibility label
enabled = actions.attribute(SEARCH_FIELD, "enabled")    # "true" or "false"
```

### `exists(locator, *, timeout=2.0) → bool`

Returns `True` if the element becomes present in the DOM within `timeout`. Checks DOM presence only, not visibility.

```python
ERROR_FIELD = (AppiumBy.ID, "com.example.app:id/error")

if actions.exists(ERROR_FIELD, timeout=1.0):
    print("Error element is in DOM:", actions.text(ERROR_FIELD))
```

---

## Scroll / swipe

### `scroll_down(*, swipe_fraction=0.5)`

Scroll the screen down (swipes upward from the center of the screen).

```python
actions.scroll_down()                    # swipe 50% of screen height
actions.scroll_down(swipe_fraction=0.7)  # bigger swipe
```

### `scroll_up(*, swipe_fraction=0.5)`

Scroll the screen up (swipes downward from the center).

```python
actions.scroll_up()
```

### `scroll_to_element(locator, *, direction="down", max_swipes=10, swipe_fraction=0.4)`

Keep scrolling until the element is visible or `max_swipes` is reached. Raises `ActionError` if element is never found.

```python
FOOTER = (AppiumBy.ACCESSIBILITY_ID, "footer_section")
actions.scroll_to_element(FOOTER, direction="down", max_swipes=15)

TOP_ELEMENT = (AppiumBy.ACCESSIBILITY_ID, "header_section")
actions.scroll_to_element(TOP_ELEMENT, direction="up")
```

### `swipe(start_x, start_y, end_x, end_y, *, duration_ms=800)`

Raw W3C Pointer swipe. Coordinates are in screen pixels.

```python
# Swipe left to dismiss a notification
actions.swipe(800, 300, 100, 300, duration_ms=400)

# Swipe from bottom to top (scroll down)
actions.swipe(400, 700, 400, 200)
```

---

## Keyboard

### `hide_keyboard()`

Dismiss the on-screen keyboard. Non-fatal if the keyboard is already hidden.

```python
actions.type_text(SEARCH, "query")
actions.hide_keyboard()
actions.tap(SEARCH_BTN)
```

### `press_keycode(keycode)`

Send an Android hardware keycode. No-op on iOS.

```python
actions.press_keycode(66)  # ENTER
actions.press_keycode(4)   # BACK
actions.press_keycode(3)   # HOME
actions.press_keycode(67)  # BACKSPACE

# Full list: developer.android.com/reference/android/view/KeyEvent
```

---

## App lifecycle / deep links

### `activate_app(app_id)`

Bring an installed app to foreground by package (Android) or bundle id (iOS).

```python
actions.activate_app("com.example.myapp")
```

### `terminate_app(app_id)`

Terminate an installed app by package/bundle id.

```python
actions.terminate_app("com.example.myapp")
```

### `background_app(seconds=1.0)`

Send app to background for the given number of seconds and return it to foreground.

```python
actions.background_app(2)
```

### `open_deep_link(url, *, app_id=None)`

Open a deep link via Appium's mobile command.
- Android uses `package` (from `app_id` or `appPackage` capability)
- iOS uses `bundleId` (from `app_id` or `bundleId` capability)

```python
actions.open_deep_link("myapp://profile", app_id="com.example.myapp")
```

---

## Hybrid / WebView context

Use these for apps that embed a web view alongside native content.

### `is_webview_available() → bool`

Check if a WEBVIEW context is currently available.

### `switch_to_webview()`

Switch the driver to the first available WEBVIEW context.

### `switch_to_native()`

Switch back to `NATIVE_APP` context.

```python
# Wait for webview, switch, interact, switch back
waiter.for_context_contains("WEBVIEW")

if actions.is_webview_available():
    actions.switch_to_webview()
    # Use standard Selenium/Appium API for web content
    el = driver.find_element(AppiumBy.CSS_SELECTOR, "#my-button")
    el.click()
    actions.switch_to_native()
```

---

## `ActionError` context

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

## Using `actions` in page objects

Inside a page class, use `self._actions`:

```python
class LoginPage(BasePage):
    _USERNAME = (AppiumBy.ID, "com.example.app:id/username")
    _PASSWORD = (AppiumBy.ID, "com.example.app:id/password")
    _LOGIN_BTN = (AppiumBy.ACCESSIBILITY_ID, "login_button")

    def log_in(self, username: str, password: str) -> None:
        self._actions.type_text(self._USERNAME, username)
        self._actions.type_text(self._PASSWORD, password)
        self._actions.tap(self._LOGIN_BTN)

    def is_loaded(self) -> bool:
        return self._actions.is_displayed(self._USERNAME)
```
