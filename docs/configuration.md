# Configuration

Settings are loaded from three sources in this order (higher wins):

```
defaults in AppiumPytestKitSettings
        ↓
.env file / environment variables
        ↓
pytest CLI flags (highest priority)
```

This lets you keep safe defaults in `.env` and override specific values per CI run or per command.

---

## The `.env` file

By default the framework reads `.env` in the directory where `pytest` is invoked.

Generate a starter `.env`:

```bash
appium-pytest-kit-init
```

Or scaffold the full project (also creates `.env`):

```bash
appium-pytest-kit-init --framework --root my-project
```

Use a custom path:

```bash
pytest --app-env-file /path/to/staging.env
```

---

## All settings

### Platform and server

| `.env` key | Python field | Type | Default | Description |
|---|---|---|---|---|
| `APP_PLATFORM` | `platform` | `android\|ios` | `android` | Target platform. Case-insensitive. |
| `APP_APPIUM_URL` | `appium_url` | `str` | `http://127.0.0.1:4723` | Appium server URL used when not managing a local server |
| `APP_MANAGE_APPIUM_SERVER` | `manage_appium_server` | `bool` | `false` | Start a local Appium process automatically |
| `APP_APPIUM_HOST` | `appium_host` | `str` | `127.0.0.1` | Host for the managed Appium server |
| `APP_APPIUM_PORT` | `appium_port` | `int` | `4723` | Port for the managed Appium server |
| `APP_APPIUM_BASE_PATH` | `appium_base_path` | `str` | `/` | Base path for the managed Appium server |
| `APP_APPIUM_SERVER_ARGS` | `appium_server_args` | comma-sep string | `""` | Extra CLI args passed to managed Appium |
| `APP_APPIUM_START_TIMEOUT` | `appium_start_timeout` | `float` | `20.0` | Seconds to wait for managed server to start |

### Device targeting

| `.env` key | Python field | Type | Default | Description |
|---|---|---|---|---|
| `APP_DEVICE_NAME` | `device_name` | `str\|None` | `None` | Device name — e.g. `"Pixel 7"` or `"iPhone 15 Pro"`. Leave blank for auto-detection. |
| `APP_PLATFORM_VERSION` | `platform_version` | `str\|None` | `None` | OS version on the device — e.g. `"14"` (Android) or `"17.4"` (iOS). Leave blank for auto. |
| `APP_UDID` | `udid` | `str\|None` | `None` | Unique device identifier. Required when multiple devices are connected. |
| `APP_IS_SIMULATOR` | `is_simulator` | `bool` | `false` | Marks the target as an iOS simulator (affects video recording) |
| `APP_DEVICE_PROFILE` | `device_profile` | `str\|None` | `None` | Named profile from `devices.yaml` — e.g. `"pixel7"` |
| `APP_DEVICES_YAML` | `devices_yaml` | `str` | `data/devices.yaml` | Path to the device profiles YAML file |

### App under test

| `.env` key | Python field | Type | Default | Description |
|---|---|---|---|---|
| `APP_APP` | `app` | `str\|None` | `None` | Full path to `.apk` or `.ipa` to install and launch |
| `APP_APP_PACKAGE` | `app_package` | `str\|None` | `None` | Android: app package — e.g. `com.example.myapp` |
| `APP_APP_ACTIVITY` | `app_activity` | `str\|None` | `None` | Android: launch activity — e.g. `.MainActivity` |
| `APP_BUNDLE_ID` | `bundle_id` | `str\|None` | `None` | iOS: bundle ID — e.g. `com.example.MyApp` |
| `APP_AUTOMATION_NAME` | `automation_name` | `str\|None` | `None` | Override automation name. Defaults: `UiAutomator2` (Android), `XCUITest` (iOS) |

### Session and capabilities

| `.env` key | Python field | Type | Default | Description |
|---|---|---|---|---|
| `APP_SESSION_MODE` | `session_mode` | `clean\|clean-session\|debug` | `clean` | Driver lifecycle mode — see [Session modes →](session-modes.md) |
| `APP_NEW_COMMAND_TIMEOUT` | `new_command_timeout` | `int` | `120` | Appium session timeout in seconds |
| `APP_NO_RESET` | `no_reset` | `bool` | `false` | Skip app state reset between sessions |
| `APP_FULL_RESET` | `full_reset` | `bool` | `false` | Uninstall and reinstall the app between sessions |
| `APP_IMPLICIT_WAIT` | `implicit_wait` | `float` | `0.0` | Appium-level implicit wait in seconds (keep at 0 and use explicit waits instead) |
| `APP_EXPLICIT_WAIT_TIMEOUT` | `explicit_wait_timeout` | `float` | `10.0` | Default timeout for `Waiter` and `MobileActions` explicit waits |
| `APP_CAPABILITIES_JSON` | `capabilities_json` | JSON object | `{}` | Extra capabilities merged last — takes highest precedence |

### Artifacts and reporting

| `.env` key | Python field | Type | Default | Description |
|---|---|---|---|---|
| `APP_ARTIFACTS_DIR` | `artifacts_dir` | `str` | `artifacts` | Root directory for screenshots, page source, and videos |
| `APP_VIDEO_POLICY` | `video_policy` | `always\|failed\|never` | `never` | When to record and save video |
| `APP_REPORTING_ENABLED` | `reporting_enabled` | `bool` | `false` | Write a JSON summary report after the session |
| `APP_REPORT_DIR` | `report_dir` | `str` | `artifacts/appium-pytest-kit` | Directory for the JSON report |

---

## Android minimal config

```env
APP_PLATFORM=android
APP_APPIUM_URL=http://127.0.0.1:4723

# Option A — launch by installed package (most common for testing)
APP_APP_PACKAGE=com.example.myapp
APP_APP_ACTIVITY=.MainActivity
APP_NO_RESET=true

# Option B — install and launch an APK
APP_APP=/path/to/myapp.apk

# Device (leave blank to auto-detect, or fill in for reliability)
APP_DEVICE_NAME=emulator-5554
APP_PLATFORM_VERSION=14
```

## iOS minimal config

```env
APP_PLATFORM=ios
APP_APPIUM_URL=http://127.0.0.1:4723

# Option A — launch by bundle ID (already installed app)
APP_BUNDLE_ID=com.example.MyApp
APP_NO_RESET=true

# Option B — install from IPA file
APP_APP=/path/to/MyApp.ipa

# Simulator
APP_DEVICE_NAME=iPhone 15 Pro
APP_PLATFORM_VERSION=17.4
APP_IS_SIMULATOR=true
```

---

## CLI overrides

Every setting can be overridden at the `pytest` command line without editing `.env`:

```bash
pytest --app-platform ios
pytest --app-appium-url http://192.168.1.10:4723
pytest --app-device-name "Pixel 7"
pytest --app-platform-version "14"
pytest --app-udid emulator-5554
pytest --app-app /path/to/app.apk
pytest --app-app-package com.example.app
pytest --app-app-activity .MainActivity
pytest --app-bundle-id com.example.ios
pytest --app-session-mode clean-session
pytest --app-device-profile pixel7
pytest --app-video-policy failed
pytest --app-is-simulator
pytest --app-manage-appium-server
pytest --app-reporting-enabled
pytest --app-capabilities-json '{"autoGrantPermissions": true}'
pytest --app-explicit-wait-timeout 15
```

For any setting without a named flag, use `--app-override`:

```bash
pytest --app-override APP_NEW_COMMAND_TIMEOUT=60
pytest --app-override noReset=true --app-override autoGrantPermissions=true
```

`--app-override` accepts `KEY=VALUE` in any of these forms:
- `APP_FIELD_NAME=value` — env-style, `APP_` prefix stripped automatically
- `field_name=value` — Python field name

---

## `APP_CAPABILITIES_JSON`

Add any capability that doesn't have a dedicated field:

```env
APP_CAPABILITIES_JSON={"autoGrantPermissions": true, "language": "en", "locale": "US"}
```

Capabilities in this JSON are merged **last**, so they override any field-derived capability.

---

## Configuration in CI

### GitHub Actions example

```yaml
- name: Run tests
  env:
    APP_PLATFORM: android
    APP_APPIUM_URL: http://127.0.0.1:4723
    APP_APP_PACKAGE: com.example.myapp
    APP_APP_ACTIVITY: .MainActivity
    APP_UDID: emulator-5554
  run: pytest -m integration --app-reporting-enabled
```

Or pass as CLI flags:

```yaml
- name: Run tests
  run: |
    pytest -m integration \
      --app-platform android \
      --app-udid emulator-5554 \
      --app-app-package com.example.myapp \
      --app-app-activity .MainActivity \
      --app-reporting-enabled
```

---

## Next steps

- [Fixtures →](fixtures.md) — what fixtures are available and how to use them
- [Page objects guide →](page-objects.md) — structuring your test code
