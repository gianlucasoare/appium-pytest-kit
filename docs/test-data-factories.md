# Test Data Factories

Generate unique, realistic test data per run to avoid collisions between parallel workers, repeat runs, and shared environments. No more `testuser1` / `test@test.com` hardcoded everywhere.

---

## The problem

Hardcoded test data causes:

- **Parallel collisions** — two xdist workers both try to register `testuser1`
- **Dirty state** — previous run left `testuser1` in the database, new run fails on duplicate
- **Unrealistic data** — `aaa@bbb.com` doesn't catch format validation bugs

## The solution

```python
from appium_pytest_kit import DataFactory

factory = DataFactory()
user = factory.user()
# {'id': 'user_a3b7c2d1', 'email': 'user_k7m2x9p3@test.example.com',
#  'username': 'testuser_h4j6n8', 'password': 'Xk3$mP9nWq2!',
#  'phone': '+15557829364', 'full_name': 'Alice Johnson'}
```

Every call generates unique data. No collisions, no cleanup needed.

---

## Quick start

### Standalone functions

For simple one-off data generation:

```python
from appium_pytest_kit.test_data import (
    random_email,
    random_username,
    random_password,
    random_phone,
    random_string,
    random_int,
    unique_id,
)

email = random_email()                    # user_k7m2x9p3@test.example.com
username = random_username()              # testuser_h4j6n8
password = random_password()             # Xk3$mP9nWq2!
phone = random_phone()                   # +15557829364
code = random_string(6, prefix="OTP-")   # OTP-a3b7c2
order_id = unique_id(prefix="order")     # order_f9e2c4a1
```

### DataFactory class

For structured, multi-field data with optional seed-based reproducibility:

```python
from appium_pytest_kit import DataFactory

factory = DataFactory()
user = factory.user()
address = factory.address()
card = factory.credit_card()
```

---

## DataFactory API

### Constructor

```python
factory = DataFactory(
    seed=42,                             # optional: reproducible output
    email_domain="staging.example.com",  # custom email domain
    phone_country_code="+44",            # custom phone prefix
)
```

| Parameter | Default | Description |
|---|---|---|
| `seed` | `None` | Random seed for deterministic output |
| `email_domain` | `test.example.com` | Email domain suffix |
| `phone_country_code` | `+1` | Phone number country code |

### Methods

#### `user(**overrides) → dict`

Generate a complete user profile:

```python
user = factory.user()
# Keys: id, email, username, password, phone, full_name

# Override specific fields
user = factory.user(email="fixed@example.com", phone="+1234567890")
```

#### `address(**overrides) → dict`

Generate a random US address:

```python
addr = factory.address()
# Keys: street, city, state, zip_code, country

addr = factory.address(city="New York", state="NY")
```

#### `credit_card(**overrides) → dict`

Generate test credit card data (standard test numbers that never charge):

```python
card = factory.credit_card()
# Keys: number, expiry, cvv, holder_name
# number is always a standard test card (Visa 4111..., etc.)
```

#### `batch_users(count, **shared_overrides) → list[dict]`

Generate multiple unique users at once:

```python
users = factory.batch_users(10)
# 10 users, all with unique emails/usernames/phones

users = factory.batch_users(5, phone="+1111111111")
# 5 users sharing the same phone, unique everything else
```

#### Primitive generators

```python
factory.email()          # user_k7m2x9p3@test.example.com
factory.username()       # testuser_h4j6n8
factory.password()       # Xk3$mP9nWq2!
factory.phone()          # +15557829364
factory.full_name()      # Alice Johnson
```

---

## Standalone functions

These use the global `random` module (not seeded by default):

| Function | Example output | Description |
|---|---|---|
| `random_string(8)` | `a3b7c2d1` | Alphanumeric string |
| `random_string(4, prefix="OTP-")` | `OTP-x7k2` | With prefix |
| `random_email()` | `user_a3b7@test.example.com` | Unique email |
| `random_phone()` | `+15557829364` | Random phone |
| `random_username()` | `testuser_h4j6n8` | Unique username |
| `random_password()` | `Xk3$mP9nWq2!` | Complex password |
| `random_int(1, 100)` | `42` | Random integer |
| `random_choice(["a","b"])` | `"b"` | Random pick |
| `unique_id(prefix="order")` | `order_f9e2c4a1` | UUID-based ID |
| `timestamp_id()` | `ts_1711660800_a3b7` | Timestamp-based ID |

---

## Seeded factories for reproducibility

When debugging a test failure, you want the exact same data that caused it:

```python
# In conftest.py
import pytest
from appium_pytest_kit import DataFactory

@pytest.fixture
def data(request):
    """Seeded factory — same data every run for this test."""
    seed = hash(request.node.nodeid) % (2**31)
    return DataFactory(seed=seed)
```

```python
def test_registration(data):
    user = data.user()
    # Always the same user for this specific test, different per test
```

---

## xdist-safe patterns

Each worker gets unique data automatically because `DataFactory` is unseeded by default:

```python
@pytest.fixture
def factory():
    return DataFactory()  # unique per worker, per call

def test_signup(factory, actions):
    user = factory.user()
    actions.type_text(EMAIL_FIELD, user["email"])     # unique email
    actions.type_text(PASSWORD_FIELD, user["password"])
    actions.tap(REGISTER_BTN)
```

---

## Integration with data-driven tests

Combine factories with `@from_file` for template-based parametrize:

```yaml
# data/signup_cases.yaml
- name: valid signup
  role: user
  expected: success

- name: admin signup
  role: admin
  expected: success
```

```python
from appium_pytest_kit import from_file, DataFactory

@from_file("data/signup_cases.yaml")
def test_signup(case, actions):
    factory = DataFactory()
    user = factory.user()

    actions.type_text(EMAIL_FIELD, user["email"])
    actions.type_text(PASSWORD_FIELD, user["password"])
    # case["role"] comes from YAML, user details are generated
    select_role(actions, case["role"])
    actions.tap(REGISTER_BTN)
    assert_screen(actions, case["expected"])
```

---

## Importing

```python
from appium_pytest_kit import DataFactory

from appium_pytest_kit.test_data import (
    random_string,
    random_email,
    random_phone,
    random_username,
    random_password,
    random_int,
    random_choice,
    unique_id,
    timestamp_id,
)
```
