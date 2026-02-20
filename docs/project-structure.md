# Project Structure

This guide explains the recommended layout for a test project built with `appium-pytest-kit`, what each file does, and how to get everything in place quickly.

---

## Recommended layout

```
my-app-tests/
├── .env                        # active configuration (device, app, Appium URL)
├── .env.example                # reference copy — commit this, not .env
├── .gitignore                  # exclude .env and artifacts/
├── conftest.py                 # project-wide fixtures and hook implementations
├── pytest.ini                  # pytest options and marker definitions
│
├── pages/                      # page object classes
│   ├── __init__.py
│   ├── base_page.py            # common BasePage all pages inherit
│   ├── login_page.py
│   └── home_page.py
│
├── flows/                      # reusable multi-step sequences (optional)
│   ├── __init__.py
│   └── auth_flow.py
│
├── data/                       # test data and device profiles
│   ├── devices.yaml            # named device profiles
│   └── test_users.json         # (optional) test data
│
├── tests/
│   ├── __init__.py
│   ├── android/
│   │   ├── __init__.py
│   │   ├── test_login.py
│   │   └── test_home.py
│   └── ios/
│       ├── __init__.py
│       └── test_login.py
│
└── artifacts/                  # auto-created on failure — do not commit
    ├── screenshots/
    ├── pagesource/
    ├── device_logs/
    └── videos/
```

---

## What each file does

### `.env`

Holds your device and app configuration. Never commit this file — it often contains paths specific to your machine.

```env
APP_PLATFORM=android
APP_APPIUM_URL=http://127.0.0.1:4723
APP_APP_PACKAGE=com.example.myapp
APP_APP_ACTIVITY=.MainActivity
APP_DEVICE_NAME=emulator-5554
APP_PLATFORM_VERSION=14
```

See [Configuration →](configuration.md) for all available settings.

### `.env.example`

A committed copy of `.env` with placeholder values. Team members clone the repo and copy this to `.env` with real values.

### `conftest.py`

The heart of your test setup. Contains:
- Framework hook implementations (capabilities, settings overrides)
- Custom fixtures shared across all tests
- Any shared constants (locators, test data)

See [conftest guide →](conftest-guide.md) for a complete walkthrough.

### `pytest.ini`

Minimal configuration:

```ini
[pytest]
addopts = -ra --strict-markers
testpaths = tests
markers =
    smoke: fast smoke-check tests
    regression: full regression suite
    android: android-only tests
    ios: ios-only tests
    integration: requires a running Appium server and connected device
```

### `pages/`

Page Object classes. Each page maps to a screen in your app and exposes named methods instead of raw locators.

See [Page objects guide →](page-objects.md) for the full walkthrough.

### `flows/`

Optional — multi-step sequences that span more than one page:

```python
# flows/auth_flow.py
class AuthFlow:
    def __init__(self, login_page, home_page):
        self._login = login_page
        self._home = home_page

    def log_in(self, username: str, password: str) -> None:
        self._login.enter_credentials(username, password)
        self._login.submit()
        self._home.wait_until_loaded()
```

### `data/devices.yaml`

Named device profiles for the 3-tier device resolver:

```yaml
devices:
  pixel7:
    device_name: "Pixel 7"
    platform: android
    udid: "emulator-5554"
    platform_version: "14"
    automation_name: UiAutomator2
    is_simulator: false

  iphone15_sim:
    device_name: "iPhone 15 Pro"
    platform: ios
    platform_version: "17.4"
    automation_name: XCUITest
    is_simulator: true
```

Select a profile at runtime: `pytest --app-device-profile pixel7`

---

## Scaffold with the CLI

Generate the full structure above in one command:

```bash
appium-pytest-kit-init --framework --root my-app-tests
```

This creates all directories and starter files. Existing files are never overwritten (use `--force` to override).

After scaffolding:

```
my-app-tests/
├── .env                  ← edit this with your device details
├── .env.example          ← commit this as the reference
├── .gitignore
├── conftest.py           ← ready to extend
├── pytest.ini
├── data/devices.yaml     ← edit or remove unused profiles
├── pages/
│   ├── base_page.py      ← keep this as-is
│   └── example_page.py   ← rename and adapt to your first screen
├── flows/
├── tests/
│   ├── android/test_smoke.py
│   └── ios/test_smoke.py
```

**First steps after scaffolding:**

1. Edit `.env` — fill in `APP_PLATFORM`, `APP_APP_PACKAGE`/`APP_BUNDLE_ID`, device details
2. Edit `data/devices.yaml` — update UDIDs to match your connected devices
3. Rename `pages/example_page.py` to match your first app screen
4. Run the smoke test: `pytest tests/android/test_smoke.py -v`

---

## `.gitignore` recommendations

```gitignore
# secrets
.env

# artifacts (auto-created by the framework on test failure)
artifacts/

# Python
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/
```

---

## Next steps

- [Configuration →](configuration.md) — all settings explained
- [Page objects guide →](page-objects.md) — building page classes step by step
- [conftest guide →](conftest-guide.md) — what to write in conftest.py
