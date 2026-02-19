# my-app — example test project template

A template for building mobile test projects with `appium-pytest-kit`.
Copy this folder, swap in your real locators, and start testing.

## Structure

```
my-app/
├── .env.example          # copy to .env and fill in your device/app details
├── conftest.py           # page fixtures, hook implementations
├── pytest.ini
├── pages/
│   ├── base_page.py      # shared base all pages inherit
│   ├── login_page.py
│   ├── home_page.py
│   └── profile_page.py
└── tests/
    ├── test_login.py
    ├── test_home.py
    └── test_profile.py
```

## Setup

```bash
cp .env.example .env
# edit .env with your device UDID, app package, etc.
```

## How to adapt this template

1. **Locators** — open each file in `pages/` and replace every
   `com.example.myapp:id/...` string with the real resource IDs from your app.
   Use [Appium Inspector](https://github.com/appium/appium-inspector) to find them.

2. **Credentials** — update `TEST_USERNAME` / `TEST_PASSWORD` in `conftest.py`,
   or load them from `.env` via `APP_CAPABILITIES_JSON`.

3. **Add pages** — copy `login_page.py` as a starting point for each new screen.
   Inherit `BasePage`, define locators and actions, done.

4. **Add fixtures** — add a new `@pytest.fixture` in `conftest.py` for each page.
   Compose fixtures (like `logged_in_home`) to avoid repeating login steps.

5. **Add tests** — create a new `tests/test_<screen>.py` file per screen.

## Run

```bash
# collection check (no device needed)
pytest --collect-only

# run all integration tests
pytest -m integration -v

# run a single test file
pytest tests/test_login.py -m integration -v

# override device at runtime
pytest -m integration --app-udid emulator-5556
```
