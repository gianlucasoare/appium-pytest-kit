# Soft Assertions

Soft assertions let you collect multiple failures in a single test without stopping at the first one. This is essential for form validation, screen state verification, and any test that checks several things at once.

---

## Why soft assertions?

With normal `assert`, your test stops at the first failure:

```python
def test_login_screen(actions):
    assert actions.text(TITLE) == "Login"        # ❌ stops here
    assert actions.is_displayed(USERNAME_FIELD)   # never checked
    assert actions.is_displayed(PASSWORD_FIELD)   # never checked
    assert actions.is_enabled(SUBMIT_BTN)         # never checked
```

You only learn about one problem per test run. With soft assertions, you learn about **all** problems at once:

```python
from appium_pytest_kit import soft_assertions

def test_login_screen(actions):
    with soft_assertions() as sa:
        sa.check_equal(actions.text(TITLE), "Login", label="title")
        sa.check_true(actions.is_displayed(USERNAME_FIELD), label="username")
        sa.check_true(actions.is_displayed(PASSWORD_FIELD), label="password")
        sa.check_true(actions.is_enabled(SUBMIT_BTN), label="submit_btn")
    # raises SoftAssertionError listing ALL failures
```

---

## Quick start

### Context manager (recommended)

```python
from appium_pytest_kit import soft_assertions

def test_profile_screen(actions):
    with soft_assertions() as sa:
        sa.check_equal(actions.text(NAME_LABEL), "John Doe", label="name")
        sa.check_contains(actions.text(EMAIL_LABEL), "@", label="email_format")
        sa.check_true(actions.is_displayed(AVATAR), label="avatar_visible")
        sa.check_not_none(actions.attribute(AVATAR, "src"), label="avatar_src")
```

### Manual usage

```python
from appium_pytest_kit import SoftAssert

def test_form_fields(actions):
    sa = SoftAssert()
    sa.check_equal(actions.count(INPUT_FIELDS), 5, label="field_count")
    sa.check_true(actions.is_enabled(SUBMIT), label="submit_enabled")
    sa.assert_all()  # raises if anything failed, then resets
```

---

## Available check methods

### `check(condition, message, *, label, expected, actual)`

The fundamental method. All other methods are shorthands built on this.

```python
sa.check(price > 0, "price must be positive", label="price", expected="> 0", actual=price)
```

### `check_equal(actual, expected, message, *, label)`

Assert `actual == expected`.

```python
sa.check_equal(title, "Home", label="page_title")
```

### `check_true(value, message, *, label)`

Assert `bool(value)` is `True`.

```python
sa.check_true(actions.is_displayed(ELEMENT), label="element_visible")
```

### `check_false(value, message, *, label)`

Assert `bool(value)` is `False`.

```python
sa.check_false(actions.is_displayed(ERROR_BANNER), label="no_error")
```

### `check_in(member, container, message, *, label)`

Assert `member in container`.

```python
sa.check_in("admin", user_roles, label="has_admin_role")
```

### `check_not_none(value, message, *, label)`

Assert `value is not None`.

```python
sa.check_not_none(actions.attribute(AVATAR, "src"), label="avatar_src")
```

### `check_gt(actual, threshold, message, *, label)`

Assert `actual > threshold`.

```python
sa.check_gt(item_count, 0, label="has_items")
```

### `check_lt(actual, threshold, message, *, label)`

Assert `actual < threshold`.

```python
sa.check_lt(response_time, 3.0, label="fast_response")
```

### `check_contains(haystack, needle, message, *, label)`

Assert `needle in haystack` for strings.

```python
sa.check_contains(welcome_text, "Hello", label="greeting")
```

---

## Inspection API

```python
sa = SoftAssert()
sa.check(False, "one")
sa.check(False, "two")

sa.failed          # True
sa.failure_count   # 2
sa.failures        # [AssertionFailure(...), AssertionFailure(...)]
```

Each `AssertionFailure` has:

| Attribute | Type | Description |
|---|---|---|
| `.message` | `str` | Failure description |
| `.label` | `str \| None` | Short tag for identification |
| `.expected` | `object` | Expected value |
| `.actual` | `object` | Actual value |

---

## Error output

When soft assertions fail, the error message lists every failure with context:

```
appium_pytest_kit.soft_assertions.SoftAssertionError: 3 soft assertion(s) failed:
  [1] (page_title) Expected 'Home', got 'Login'
        expected='Home'  actual='Login'
  [2] (submit_btn) Expected truthy value
        expected=True  actual=False
  [3] (item_count) Expected 5, got 3
        expected=5  actual=3
```

---

## Real-world patterns

### Form validation (check all fields at once)

```python
def test_registration_form(actions):
    with soft_assertions() as sa:
        sa.check_true(actions.is_displayed(FIRST_NAME), label="first_name")
        sa.check_true(actions.is_displayed(LAST_NAME), label="last_name")
        sa.check_true(actions.is_displayed(EMAIL), label="email")
        sa.check_true(actions.is_displayed(PASSWORD), label="password")
        sa.check_true(actions.is_displayed(CONFIRM_PW), label="confirm_password")
        sa.check_true(actions.is_enabled(REGISTER_BTN), label="register_btn")
        sa.check_equal(actions.count(REQUIRED_MARKERS), 5, label="required_count")
```

### Post-action state verification

```python
def test_add_to_cart(actions):
    actions.tap(ADD_TO_CART_BTN)

    with soft_assertions() as sa:
        sa.check_equal(actions.text(CART_BADGE), "1", label="cart_count")
        sa.check_true(actions.is_displayed(SUCCESS_TOAST), label="toast_shown")
        sa.check_equal(actions.text(TOTAL), "$9.99", label="total_price")
```

### Midpoint checkpoints

```python
def test_checkout_flow(actions):
    sa = SoftAssert()

    # Step 1: Cart
    sa.check_gt(int(actions.text(CART_COUNT)), 0, label="cart_not_empty")
    actions.tap(CHECKOUT_BTN)

    # Step 2: Shipping
    sa.check_true(actions.is_displayed(SHIPPING_FORM), label="shipping_visible")
    actions.type_text(ADDRESS, "123 Main St")
    actions.tap(CONTINUE_BTN)

    # Step 3: Payment
    sa.check_true(actions.is_displayed(PAYMENT_FORM), label="payment_visible")

    sa.assert_all()  # all accumulated checks evaluated here
```

---

## Importing

```python
from appium_pytest_kit import (
    SoftAssert,           # manual usage
    SoftAssertionError,   # error class
    AssertionFailure,     # failure record type
    soft_assertions,      # context manager
)
```
