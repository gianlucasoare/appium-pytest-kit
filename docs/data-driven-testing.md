# Data-driven testing

appium-pytest-kit provides helpers for loading test data from YAML/JSON files and generating parametrized test cases.

## Quick start

Create a test data file:

```yaml
# data/login_cases.yaml
- name: valid login
  username: user@example.com
  password: Test1234!
  expected: home

- name: invalid password
  username: user@example.com
  password: wrong
  expected: error

- name: empty username
  username: ""
  password: Test1234!
  expected: error
```

Use it in a test:

```python
from appium_pytest_kit import from_file

@from_file("data/login_cases.yaml")
def test_login(case, login_page):
    login_page.login(case["username"], case["password"])
    assert login_page.current_screen() == case["expected"]
```

This generates three test cases named `test_login[valid login]`, `test_login[invalid password]`, and `test_login[empty username]`.

## Loading data manually

Use `load_test_data()` when you need more control:

```python
from appium_pytest_kit import load_test_data

cases = load_test_data("data/login_cases.yaml")
# Returns: [{"name": "valid login", ...}, {"name": "invalid password", ...}, ...]
```

### Platform-specific data

Structure your file with platform keys:

```yaml
# data/deep_links.yaml
android:
  - name: home screen
    url: myapp://home
  - name: profile
    url: myapp://profile

ios:
  - name: home screen
    url: https://myapp.example.com/home
  - name: profile
    url: https://myapp.example.com/profile
```

Load with a platform filter:

```python
cases = load_test_data("data/deep_links.yaml", platform="android")
# Returns only the android cases
```

Or use it with the decorator:

```python
@from_file("data/deep_links.yaml", platform="android")
def test_deep_link(case, actions):
    actions.open_deep_link(case["url"])
```

### Nested sections

Use the `key` parameter to select a named section:

```yaml
# data/test_data.yaml
smoke:
  - name: basic login
    username: user@example.com
    password: Test1234!

regression:
  - name: special characters
    username: "user+test@example.com"
    password: "p@ss!w0rd#$"
```

```python
cases = load_test_data("data/test_data.yaml", key="smoke")
```

## Cross-platform tests

Use `cross_platform()` to run the same test on both Android and iOS:

```python
from appium_pytest_kit import cross_platform

@cross_platform()
def test_login_works(platform, login_page):
    login_page.login("user@example.com", "Test1234!")
    assert login_page.is_on_home()
```

This generates `test_login_works[android]` and `test_login_works[ios]`.

## JSON support

All helpers accept `.json` files with the same structure:

```json
[
  {"name": "valid login", "username": "user@example.com", "password": "Test1234!"},
  {"name": "invalid password", "username": "user@example.com", "password": "wrong"}
]
```

## Custom test IDs

By default, the `name` field in each case is used as the test ID. Change this with `id_field`:

```python
@from_file("data/cases.yaml", id_field="scenario")
def test_checkout(case, cart_page):
    ...
```

## Requirements

- YAML support requires the `yaml` extra: `pip install appium-pytest-kit[yaml]`
- JSON files work with no extra dependencies
