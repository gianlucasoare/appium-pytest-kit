# Troubleshooting

---

## Enabling debug logs

`appium-pytest-kit` uses Python's standard `logging` module with the logger hierarchy `appium_pytest_kit.*`. No configuration is needed — just tell pytest to surface the logs:

```bash
# Print all INFO+ logs live in the terminal
pytest --log-cli-level=INFO

# Full debug trace (every wait, every action, every lifecycle event)
pytest --log-cli-level=DEBUG

# Capture logs in the report but only show on failure
pytest --log-level=DEBUG
```

You can also set this permanently in `pyproject.toml` or `pytest.ini`:

```toml
# pyproject.toml
[tool.pytest.ini_options]
log_cli       = true
log_cli_level = "INFO"
log_level     = "DEBUG"   # also captured in failure output
```

### What each level shows

| Level | Logger | Example message |
|---|---|---|
| `INFO` | `appium_pytest_kit.pytest_plugin` | `driver:created  session=abc123  platform=android  node=tests/test_login.py::test_valid` |
| `INFO` | `appium_pytest_kit.pytest_plugin` | `driver:reuse  session=abc123  node=...` (retry keeping session alive) |
| `INFO` | `appium_pytest_kit.pytest_plugin` | `driver:quit  session=abc123  node=...` |
| `INFO` | `appium_pytest_kit.pytest_plugin` | `retry:keep-alive  attempt=1/2  node=...` |
| `INFO` | `appium_pytest_kit.pytest_plugin` | `artifact:screenshot  artifacts/screenshots/test_foo.png` |
| `INFO` | `appium_pytest_kit.pytest_plugin` | `artifact:video  artifacts/videos/test_foo.mp4` |
| `INFO` | `appium_pytest_kit._internal.device_resolver` | `device:tier-1 (explicit)  name='Pixel 7'  udid=emulator-5554` |
| `INFO` | `appium_pytest_kit._internal.server` | `server:starting  host=127.0.0.1  port=4723  timeout=30000ms` |
| `INFO` | `appium_pytest_kit._internal.video` | `video:started` |
| `DEBUG` | `appium_pytest_kit.waits` | `wait:visibility  ('id', 'username')  timeout=10.0s` |
| `DEBUG` | `appium_pytest_kit.waits` | `wait:clickable  ('accessibility id', 'login_btn')  timeout=10.0s` |
| `DEBUG` | `appium_pytest_kit.actions` | `tap  ('accessibility id', 'submit_button')` |
| `DEBUG` | `appium_pytest_kit.actions` | `type_text  ('id', 'username')  value='testuser'  clear_first=True` |
| `DEBUG` | `appium_pytest_kit.actions` | `assert:text  ('id', 'result')  expected='42'` |
| `DEBUG` | `appium_pytest_kit.actions` | `swipe  (400,700)->(400,200)  duration=800ms` |

### Typical CI failure output (INFO level)

```
INFO  appium_pytest_kit.device_resolver:  device:resolving  platform=android
INFO  appium_pytest_kit.device_resolver:  device:tier-1 (explicit)  name='emulator-5554'  udid=emulator-5554
INFO  appium_pytest_kit.pytest_plugin:    driver:created  session=4f2a1b  platform=android  node=tests/test_login.py::test_valid
INFO  appium_pytest_kit.video:            video:started
FAILED tests/test_login.py::test_valid
INFO  appium_pytest_kit.pytest_plugin:    artifact:screenshot  artifacts/screenshots/test_valid.png
INFO  appium_pytest_kit.pytest_plugin:    artifact:page_source  artifacts/pagesource/test_valid.xml
INFO  appium_pytest_kit.pytest_plugin:    driver:quit  session=4f2a1b  node=tests/test_login.py::test_valid
```

---

## `DriverCreationError: Failed to create Appium session`

**Checklist:**

1. Is Appium running?
   ```bash
   curl http://127.0.0.1:4723/status
   # should return JSON with "ready": true
   ```

2. Does `APP_APPIUM_URL` match where Appium is listening?
   ```bash
   # Appium default: http://127.0.0.1:4723
   # Check the Appium console output for the actual URL
   ```

3. Is the device/emulator connected?
   ```bash
   adb devices              # Android — should show "device" not "offline"
   xcrun simctl list        # iOS — should show "Booted"
   open -a Simulator        # start iOS Simulator if needed
   ```

4. Are the capabilities correct? Check `APP_APP_PACKAGE` / `APP_BUNDLE_ID` for typos.

---

## `LaunchValidationError`

You're missing the minimum required app settings. Add to `.env`:

```env
# Android — one of these:
APP_APP=/path/to/app.apk
# or
APP_APP_PACKAGE=com.example.myapp
APP_APP_ACTIVITY=.MainActivity

# iOS — one of these:
APP_APP=/path/to/MyApp.ipa
# or
APP_BUNDLE_ID=com.example.MyApp
```

---

## `ConfigurationError: managed Appium server failed to start`

- Is `appium` on `PATH`?
  ```bash
  which appium
  appium --version
  ```
- Increase the start timeout:
  ```env
  APP_APPIUM_START_TIMEOUT=45.0
  ```
- Check Appium startup logs for the actual error

---

## `WaitTimeoutError: Element not visible`

1. **Wrong locator** — use Appium Inspector to find the correct element ID:
   - Android: `uiautomatorviewer` or Appium Inspector
   - iOS: Appium Inspector

2. **App not fully loaded** — the element may need more time:
   ```python
   waiter.for_visibility(locator, timeout=30.0)
   ```

3. **Wrong context** — in hybrid apps, you may be in the wrong context:
   ```python
   # Check available contexts
   print(driver.contexts)
   # Switch if needed
   actions.switch_to_webview()
   ```

4. **Element off-screen** — scroll to it first:
   ```python
   actions.scroll_to_element(locator)
   ```

5. **Implicit wait conflict** — if `APP_IMPLICIT_WAIT` is set, it can interfere with explicit waits. Keep it at `0.0` (default) and use `APP_EXPLICIT_WAIT_TIMEOUT` instead.

---

## Settings from `.env` are not being applied

- The `.env` file must be in the directory where `pytest` is invoked (your project root)
- Or specify the path explicitly:
  ```bash
  pytest --app-env-file /full/path/to/.env
  ```
- Variable names must be prefixed with `APP_`:
  ```env
  APP_PLATFORM=android    # correct
  PLATFORM=android        # wrong — ignored
  ```
- Check for syntax errors — no quotes around values:
  ```env
  APP_APP_PACKAGE=com.example.myapp    # correct
  APP_APP_PACKAGE="com.example.myapp"  # wrong — quotes are included in the value
  ```

---

## `platform must be 'android' or 'ios'`

`APP_PLATFORM` only accepts exactly `android` or `ios` (case-insensitive):

```env
APP_PLATFORM=android   # correct
APP_PLATFORM=Android   # also correct (normalised)
APP_PLATFORM=ANDROID   # also correct
APP_PLATFORM=mobile    # wrong — ConfigurationError
```

---

## Device profile not found

```
ConfigurationError: Device profile 'my_device' not found in data/devices.yaml.
Available: ['pixel7', 'iphone15_sim']
```

- Check the profile name spelling in `APP_DEVICE_PROFILE`
- Verify `APP_DEVICES_YAML` points to the right file
- Confirm the profile key exists in `devices.yaml` under `devices:`

---

## Multiple Android devices warning

```
UserWarning: Multiple Android devices detected (['emulator-5554', 'R3CN60FZQMK']).
The first device will be used. Set APP_UDID to target a specific device.
```

Set `APP_UDID` to avoid ambiguity:

```env
APP_UDID=emulator-5554
```

---

## Tests pass locally but fail in CI

1. **Device UDID mismatch** — CI emulators may have different serial numbers:
   ```bash
   # Print the UDID in a CI step:
   adb devices
   ```
   Then set `APP_UDID` in your CI environment variable.

2. **Platform version mismatch** — pin the emulator API level in CI and match `APP_PLATFORM_VERSION`.

3. **Timing issues** — CI machines can be slower. Increase:
   ```env
   APP_EXPLICIT_WAIT_TIMEOUT=20.0
   APP_NEW_COMMAND_TIMEOUT=180
   APP_APPIUM_START_TIMEOUT=60.0
   ```

4. **Enable reporting for CI artifact inspection:**
   ```bash
   pytest --app-reporting-enabled --app-video-policy failed
   ```

---

## `PyYAML not installed` when using device profiles

```
ConfigurationError: PyYAML is required for device profiles. Install with: pip install PyYAML
```

```bash
pip install "appium-pytest-kit[yaml]"
# or
pip install PyYAML
```

---

## Video recording not working on iOS Simulator

iOS Simulator recording is not supported by Appium. The framework skips it silently when `APP_IS_SIMULATOR=true`.

For iOS recording support, use a physical device.

---

## `app-override` flag not working

`--app-override` expects `KEY=VALUE` format:

```bash
pytest --app-override APP_NEW_COMMAND_TIMEOUT=60    # correct
pytest --app-override new_command_timeout=60        # also correct (Python field name)
pytest --app-override "new command timeout=60"      # wrong — spaces in key
```

For boolean settings, use the named flag:

```bash
pytest --app-manage-appium-server          # true
pytest --no-app-manage-appium-server       # false
```

---

## Checking the resolved configuration

Add a quick test that dumps the settings — useful for debugging:

```python
def test_print_settings(settings):
    print(f"\nPlatform:       {settings.platform}")
    print(f"Appium URL:     {settings.appium_url}")
    print(f"App package:    {settings.app_package}")
    print(f"Bundle ID:      {settings.bundle_id}")
    print(f"Device name:    {settings.device_name}")
    print(f"UDID:           {settings.udid}")
    print(f"Session mode:   {settings.session_mode}")
    print(f"Explicit wait:  {settings.explicit_wait_timeout}s")
```

Run with `-s` to see the output:

```bash
pytest test_print_settings.py -s
```
