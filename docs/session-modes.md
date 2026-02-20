# Session Modes

`APP_SESSION_MODE` controls how the Appium driver is created and destroyed across your test run.

---

## The three modes

### `clean` (default)

A **fresh Appium session** is created before each test and quit immediately after, even on failure.

```env
APP_SESSION_MODE=clean
```

**Use when:**
- Maximum test isolation is required
- Tests can affect app state (login, preferences, stored data)
- Running in CI where correctness matters more than speed

**Trade-off:** Slowest — every test pays the session startup cost (typically 3–10 seconds per test on Android, 10–20 seconds on iOS).

```
Test 1: [create session] → [test] → [quit]
Test 2: [create session] → [test] → [quit]
Test 3: [create session] → [test] → [quit]
```

---

### `clean-session`

A **single Appium session** is shared across the entire test run. The session is created before the first test and quit once at the very end.

```env
APP_SESSION_MODE=clean-session
```

**Use when:**
- Tests are independent enough to share a session (stateless UI tests, read-only tests)
- Speed is a priority
- Your app can be navigated back to a known state between tests

**Trade-off:** Tests share driver state — a test that leaves the app in a broken state can affect subsequent tests.

```
[create session]
Test 1: [test]
Test 2: [test]
Test 3: [test]
[quit session]
```

**Tip:** Combine with an `autouse` fixture that navigates to a known screen before each test:

```python
# conftest.py
@pytest.fixture(autouse=True)
def reset_to_home(actions, home_page):
    """Navigate to the home screen before each test."""
    try:
        actions.press_keycode(4)  # Android back
        home_page.wait_until_loaded(timeout=3.0)
    except Exception:
        pass  # already on home or not applicable
```

---

### `debug`

Same as `clean-session` (one shared session) but the session is **kept alive after a failure** — it is never quit automatically.

```env
APP_SESSION_MODE=debug
```

**Use when:**
- Debugging a flaky or failing test locally
- You want to inspect the device state after the test fails

**Trade-off:** The app/session is never reset. Useful only for local debugging — not suitable for CI.

```
[create session]
Test 1: [test] → ✓
Test 2: [test] → ✗ FAIL  ← session kept alive, you can inspect the device
Test 3: [test]
[session may or may not be quit at end]
```

---

## Setting the mode

### `.env`

```env
APP_SESSION_MODE=clean          # default
APP_SESSION_MODE=clean-session  # shared session
APP_SESSION_MODE=debug          # shared session + keep alive on failure
```

### CLI (overrides `.env`)

```bash
pytest --app-session-mode clean-session
pytest --app-session-mode debug
```

### `conftest.py` hook

```python
def pytest_appium_pytest_kit_configure_settings(settings):
    # Force debug mode for a specific local run
    import os
    if os.getenv("DEBUG_TESTS"):
        return settings.model_copy(update={"session_mode": "debug"})
```

---

## Mode comparison

| | `clean` | `clean-session` | `debug` |
|---|---|---|---|
| Session per test | Yes | No | No |
| Session count | N (one per test) | 1 | 1 |
| Speed | Slowest | Fastest | Fastest |
| Isolation | Maximum | None | None |
| Good for CI | Yes | Yes (stateless tests) | No |
| Good for local debug | No | No | Yes |

---

## Important: avoid `driver.quit()` in shared modes

In `clean-session` and `debug` modes, calling `driver.quit()` in a test or fixture teardown will break all subsequent tests:

```python
# BAD — kills the shared session
def test_something(driver):
    ...
    driver.quit()  # don't do this in clean-session / debug mode

# GOOD — the framework handles quit automatically
def test_something(driver):
    ...
    # just return, the framework will quit at the right time
```
