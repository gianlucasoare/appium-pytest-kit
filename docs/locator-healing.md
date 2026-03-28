# Locator Healing

Locator healing provides fallback chains for UI elements. When a primary locator breaks (after an app update, for example), the framework automatically tries alternative locators before failing the test. This dramatically reduces test maintenance cost.

---

## The problem

Locators break. App updates rename IDs, restructure layouts, or change accessibility labels. A single locator change can break dozens of tests:

```python
# This breaks when the ID changes from btn_login to button_login
LOGIN_BTN = ("id", "com.example.app:id/btn_login")
```

## The solution

Define fallback chains. If the primary locator fails, alternatives are tried in order:

```python
from appium_pytest_kit import chain

LOGIN_BTN = chain(
    ("accessibility id", "login_button"),           # preferred: stable
    ("id", "com.example.app:id/btn_login"),         # fallback 1: resource ID
    ("xpath", "//android.widget.Button[@text='Log in']"),  # fallback 2: text
    name="login_button",
)
```

---

## Quick start

### Basic usage

```python
from appium_pytest_kit import chain

# Define a locator chain
SUBMIT = chain(
    ("accessibility id", "submit"),
    ("id", "com.example:id/submit_btn"),
    name="submit_button",
)

def test_form_submit(driver):
    result = SUBMIT.find(driver)
    result.element.click()

    if result.healed:
        print(f"⚠ Primary locator broken, used: {result.used_locator}")
```

### With MobileActions

```python
from appium_pytest_kit import chain

SUBMIT = chain(
    ("accessibility id", "submit"),
    ("id", "com.example:id/submit_btn"),
    name="submit_button",
)

def test_form_submit(actions, driver):
    # Use the chain to find, then interact via the element
    result = SUBMIT.find(driver)
    result.element.click()
```

### Optional elements

```python
PROMO_BANNER = chain(
    ("accessibility id", "promo_banner"),
    ("id", "com.example:id/banner"),
    name="promo_banner",
)

def test_home_screen(driver):
    result = PROMO_BANNER.find_or_none(driver)
    if result.element:
        result.element.click()
    # No error if banner is absent
```

---

## LocatorChain API

### Creating chains

```python
from appium_pytest_kit import LocatorChain, chain

# Using the chain() shorthand (recommended)
btn = chain(
    ("accessibility id", "login"),
    ("id", "btn_login"),
    name="login_button",
)

# Using the class directly
btn = LocatorChain(
    ("accessibility id", "login"),
    ("id", "btn_login"),
    name="login_button",
)
```

### Properties

| Property | Type | Description |
|---|---|---|
| `.primary` | `Locator` | The first (preferred) locator |
| `.fallbacks` | `tuple[Locator, ...]` | Remaining locators in priority order |
| `.all_locators` | `tuple[Locator, ...]` | All locators including primary |
| `.name` | `str \| None` | Human-readable element name |

### Methods

#### `find(driver) → HealingResult`

Try each locator in order. Returns the first match. Raises `ActionError` if all fail.

#### `find_or_none(driver) → HealingResult`

Like `find()`, but returns `HealingResult` with `element=None` instead of raising.

---

## HealingResult

Every `find()` call returns a `HealingResult`:

| Attribute | Type | Description |
|---|---|---|
| `.element` | `WebElement \| None` | The found element |
| `.used_locator` | `Locator \| None` | Which locator succeeded |
| `.original_locator` | `Locator` | The primary locator |
| `.healed` | `bool` | `True` if a fallback was used |
| `.attempts` | `int` | Number of locators tried |

```python
result = LOGIN_BTN.find(driver)
if result.healed:
    # Log this for maintenance tracking
    logger.warning("Locator healed: %s → %s", result.original_locator, result.used_locator)
```

---

## HealingRegistry

For larger projects, use a central registry to manage all locator chains:

```python
from appium_pytest_kit import HealingRegistry

registry = HealingRegistry()

# Register chains
registry.register_simple(
    "login_btn",
    ("accessibility id", "login_button"),
    ("id", "com.example:id/btn_login"),
)
registry.register_simple(
    "username",
    ("accessibility id", "username_field"),
    ("id", "com.example:id/input_username"),
)

# Look up and use
def test_login(driver):
    result = registry.find("login_btn", driver)
    result.element.click()
```

### Registry API

| Method | Description |
|---|---|
| `register(name, chain)` | Register a `LocatorChain` under a name |
| `register_simple(name, primary, *fallbacks)` | Register from raw locator tuples |
| `get(name)` | Look up a chain (raises `KeyError` if missing) |
| `find(name, driver)` | Look up and find in one call |

### Healing statistics

The registry tracks when fallback locators are used:

```python
print(registry.heal_count)        # 3
print(registry.registered_names)  # ["login_btn", "username", ...]

summary = registry.summary()
# {"total_heals": 3, "unique_elements_healed": 2, "registered_chains": 5}
```

Use this in CI to detect locator drift before it causes widespread failures.

---

## Page object integration

```python
from appium_pytest_kit import LocatorChain, chain
from pages.base_page import BasePage

class LoginPage(BasePage):
    _USERNAME = chain(
        ("accessibility id", "username_field"),
        ("id", "com.example:id/input_username"),
        name="username",
    )
    _PASSWORD = chain(
        ("accessibility id", "password_field"),
        ("id", "com.example:id/input_password"),
        name="password",
    )
    _LOGIN_BTN = chain(
        ("accessibility id", "login_button"),
        ("id", "com.example:id/btn_login"),
        ("xpath", "//android.widget.Button[@text='Log in']"),
        name="login_button",
    )

    def log_in(self, username: str, password: str) -> None:
        self._USERNAME.find(self._driver).element.send_keys(username)
        self._PASSWORD.find(self._driver).element.send_keys(password)
        self._LOGIN_BTN.find(self._driver).element.click()
```

---

## Best practices

1. **Primary locator should be the most stable** — accessibility IDs are best, then resource IDs, then XPath last
2. **Name every chain** — names appear in logs and error messages
3. **Use `find_or_none()` for optional elements** — don't let optional UI break tests
4. **Check `registry.summary()` in CI** — rising heal counts signal locator drift
5. **Keep chains in page objects or a central module** — not scattered in test files

---

## Importing

```python
from appium_pytest_kit import (
    LocatorChain,       # chain class
    HealingResult,      # result dataclass
    HealingRegistry,    # central registry
    chain,              # shorthand factory
)
```
