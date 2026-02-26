# Device Resolution

The framework resolves the target device automatically through three tiers, in priority order. You only need to configure as much as your situation requires.

---

## Priority order

```
Tier 1 (highest) — Explicit settings (APP_DEVICE_NAME / APP_UDID in .env or CLI)
        ↓
Tier 2 — Named profile from data/devices.yaml (APP_DEVICE_PROFILE)
        ↓
Tier 3 (lowest) — Auto-detect via adb (Android) or xcrun (iOS)
```

---

## Tier 1 — Explicit settings

Set device details directly in `.env` or via CLI. This is the most reliable approach and is required when multiple devices are connected.

```env
APP_DEVICE_NAME=Pixel 7
APP_UDID=emulator-5554
APP_PLATFORM_VERSION=14
```

CLI override:

```bash
pytest --app-device-name "Pixel 7" --app-udid emulator-5554
```

**When Tier 1 activates:** whenever `APP_DEVICE_NAME` or `APP_UDID` is set (either one is sufficient).

---

## Tier 2 — Named device profile

Define reusable named profiles in `data/devices.yaml`. Useful for teams where different people use different devices, or for switching between emulator/physical device.

### Step 1 — Create `data/devices.yaml`

```yaml
# data/devices.yaml
devices:
  # Android emulator (Pixel 7, API 34)
  pixel7_emu:
    device_name: "Pixel 7"
    platform: android
    udid: "emulator-5554"
    platform_version: "14"
    automation_name: UiAutomator2
    is_simulator: false

  # Physical Android device
  pixel7_phys:
    device_name: "Pixel 7"
    platform: android
    udid: "R3CN60FZQMK"        # get from: adb devices
    platform_version: "14"
    automation_name: UiAutomator2
    is_simulator: false

  # iOS simulator
  iphone15_sim:
    device_name: "iPhone 15 Pro"
    platform: ios
    platform_version: "17.4"
    automation_name: XCUITest
    is_simulator: true

  # Physical iPhone
  iphone15_phys:
    device_name: "iPhone 15 Pro"
    platform: ios
    udid: "00008120-001A..."    # get from: xcrun xctrace list devices
    platform_version: "17.4"
    automation_name: XCUITest
    is_simulator: false
```

### Step 2 — Select a profile

Via `.env`:

```env
APP_DEVICE_PROFILE=pixel7_emu
APP_DEVICES_YAML=data/devices.yaml   # default path, can omit
```

Via CLI:

```bash
pytest --app-device-profile iphone15_sim
pytest --app-device-profile pixel7_phys --app-devices-yaml /path/to/other.yaml
```

### YAML keys

| Key | Required | Description |
|---|---|---|
| `device_name` | Yes | Human-readable name passed to Appium |
| `platform` | Yes | `android` or `ios` |
| `udid` | No | Unique device ID. Required for physical devices when >1 is connected |
| `platform_version` | No | OS version string |
| `automation_name` | No | Automation driver (`UiAutomator2` / `XCUITest`) |
| `is_simulator` | No | `true` for iOS simulators (affects video recording) |

> **Requires PyYAML:** `pip install "appium-pytest-kit[yaml]"` or `pip install PyYAML`

---

## Tier 3 — Auto-detect

When neither explicit settings nor a device profile are provided, the framework tries to detect the connected device automatically.

### Android auto-detect

Runs `adb devices -l` and picks the first connected device. Device name, UDID, and Android version are read via `adb shell getprop`.

```bash
# Only works when exactly one device is connected:
pytest   # no device settings needed
```

> **Multiple devices:** If more than one Android device is connected, a warning is printed and the first one is used. Set `APP_UDID` to target a specific device.

### iOS auto-detect

1. First tries `xcrun simctl list devices --json` for a booted simulator
2. Falls back to `xcrun xctrace list devices` for a physical device

```bash
# Start a simulator first:
open -a Simulator

# Then run (no device settings needed):
pytest
```

### When auto-detect returns nothing

If no device is found, `device_info` is `None`. The driver creation will then fail with an Appium error about missing capabilities — add explicit device settings or a profile.

---

## Launch validation

Before creating an Appium session, the framework checks that the minimum required app settings are present.
If `APP_APP_AUTO_DISCOVER=true`, it also accepts the latest build discovered under `APP_APP_BUILDS_DIR`.

**Android** — requires `APP_APP` (APK path) **or** both `APP_APP_PACKAGE` + `APP_APP_ACTIVITY`:

```env
# Option A — install APK
APP_APP=/path/to/myapp.apk

# Option B — launch installed app
APP_APP_PACKAGE=com.example.myapp
APP_APP_ACTIVITY=.MainActivity

# Option C — auto-discover latest APK/AAB from app_builds/android/
APP_APP_AUTO_DISCOVER=true
APP_APP_BUILDS_DIR=app_builds
```

**iOS** — requires `APP_APP` (IPA path) **or** `APP_BUNDLE_ID`:

```env
# Option A — install IPA
APP_APP=/path/to/MyApp.ipa

# Option B — launch installed app
APP_BUNDLE_ID=com.example.MyApp

# Option C — auto-discover latest build (APP for simulator, IPA for device)
APP_APP_AUTO_DISCOVER=true
APP_APP_BUILDS_DIR=app_builds
```

If neither is configured, `LaunchValidationError` is raised with a clear message before any connection is attempted.

---

## Finding your device UDID

### Android (physical or emulator)

```bash
adb devices
# List of devices attached
# emulator-5554   device
# R3CN60FZQMK     device
```

Use the first column value as `APP_UDID`.

### iOS simulator

```bash
xcrun simctl list devices booted
# iPhone 15 Pro (17.4) (Booted)
#     UDID: 12345678-ABCD-1234-ABCD-1234567890AB
```

### iOS physical device

```bash
xcrun xctrace list devices
# iPhone 15 Pro (17.4) (00008120-001A...)
```

Or open **Xcode → Window → Devices and Simulators** and copy the identifier.
