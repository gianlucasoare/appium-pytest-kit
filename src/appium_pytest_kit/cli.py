"""Command-line utilities for appium-pytest-kit."""


import argparse
from collections.abc import Sequence
from pathlib import Path

ENV_TEMPLATE = """\
# appium-pytest-kit configuration
# Rename this file to .env (or pass --app-env-file <path> to pytest).
# Lines starting with # are comments and are ignored.

# ── Platform ────────────────────────────────────────────────────────────────
# Target mobile platform. Must be "android" or "ios".
APP_PLATFORM=android

# ── Appium server ───────────────────────────────────────────────────────────
# URL of the running Appium server.
APP_APPIUM_URL=http://127.0.0.1:4723

# Set to "true" to let the kit start and stop Appium automatically.
# When enabled, APP_APPIUM_URL is ignored and host/port below are used instead.
APP_MANAGE_APPIUM_SERVER=false

# ── Device targeting ────────────────────────────────────────────────────────
# Human-readable device name, e.g. "Pixel 7" or "iPhone 15 Pro".
# Leave blank for auto-detection (requires adb / xcrun).
APP_DEVICE_NAME=

# Device OS version, e.g. "14" (Android) or "17.4" (iOS).
# Leave blank to let Appium pick the version automatically.
APP_PLATFORM_VERSION=

# Unique device identifier (serial for Android, UDID for iOS).
# Required when multiple devices are connected at the same time.
APP_UDID=

# ── App under test ──────────────────────────────────────────────────────────
# Full path to the .apk or .ipa to install and launch.
# Leave blank if you want to launch an already-installed app by package/bundle.
APP_APP=

# Android only — package name of the installed app, e.g. "com.example.myapp".
APP_APP_PACKAGE=

# Android only — main activity to launch, e.g. ".MainActivity".
APP_APP_ACTIVITY=

# iOS only — bundle identifier of the installed app, e.g. "com.example.MyApp".
APP_BUNDLE_ID=

# ── Advanced ────────────────────────────────────────────────────────────────
# Appium base path (default "/"). Change only if your server uses a custom path.
APP_APPIUM_BASE_PATH=/

# Extra Appium capabilities as a JSON object, e.g. {"wdaLocalPort": 8100}.
APP_CAPABILITIES_JSON={}

# Driver session lifecycle strategy:
#   clean         - fresh driver per test (default; maximum isolation)
#   clean-session - one shared driver for the whole suite (faster)
#   debug         - like clean-session but keeps the session alive after failures
APP_SESSION_MODE=clean

# Explicit wait timeout in seconds used by Waiter and MobileActions (default 10).
APP_EXPLICIT_WAIT_TIMEOUT=10

# Screen recording policy:
#   never  - no recording (default)
#   failed - save video only when a test fails
#   always - save video for every test
APP_VIDEO_POLICY=never

# Set to "true" to generate a JSON summary report in artifacts/.
APP_REPORTING_ENABLED=false
"""

# ---------------------------------------------------------------------------
# Framework scaffold templates
# ---------------------------------------------------------------------------

_DEVICES_YAML = """\
devices:
  pixel7:
    device_name: "Pixel 7"
    platform: android
    udid: ""
    platform_version: "14"
    automation_name: UiAutomator2
    is_simulator: false

  iphone15:
    device_name: "iPhone 15 Pro"
    platform: ios
    udid: ""
    platform_version: "17.4"
    automation_name: XCUITest
    is_simulator: false

  iphone15_sim:
    device_name: "iPhone 15 Pro"
    platform: ios
    platform_version: "17.4"
    automation_name: XCUITest
    is_simulator: true
"""

_CONFTEST_PY = """\
\"\"\"Session-level fixtures for the test suite.\"\"\"

import pytest
from appium_pytest_kit.settings import AppiumPytestKitSettings


@pytest.fixture(scope="session")
def app_settings(settings: AppiumPytestKitSettings) -> AppiumPytestKitSettings:
    \"\"\"Expose settings to tests under a shorter alias.\"\"\"
    return settings
"""

_PYTEST_INI = """\
[pytest]
addopts = -ra --strict-config --strict-markers
testpaths = tests
markers =
    smoke: fast smoke tests
    regression: full regression suite
    android: android-only tests
    ios: ios-only tests
"""

_BASE_PAGE = """\
\"\"\"Abstract base class for all page objects.\"\"\"

from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.waits import Waiter


class BasePage:
    \"\"\"Thin composition base providing driver, waiter and actions.\"\"\"

    def __init__(self, driver, waiter: Waiter, actions: MobileActions) -> None:
        self._driver = driver
        self._waiter = waiter
        self._actions = actions
"""

_EXAMPLE_PAGE = """\
\"\"\"Example page object — replace with your own app pages.\"\"\"

from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage

_BY = AppiumBy.ACCESSIBILITY_ID


class ExamplePage(BasePage):
    \"\"\"Replace with real locators for your app.\"\"\"

    _TITLE = (_BY, "example_title")

    def is_loaded(self, *, timeout: float = 10.0) -> bool:
        \"\"\"Return True when the page title is visible.\"\"\"
        try:
            self._waiter.for_visibility(self._TITLE, timeout=timeout)
            return True
        except Exception:
            return False
"""

_BASE_FLOW = """\
\"\"\"Base class for all flows.\"\"\"


from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.waits import Waiter


class BaseFlow:
    \"\"\"Thin composition base providing driver, waiter and actions.

    Flows orchestrate multi-page journeys. Unlike page objects (which model
    a single screen), a flow coordinates several pages to complete a user
    journey — e.g. "log in, open settings, change language, log out".
    \"\"\"

    def __init__(self, driver, waiter: Waiter, actions: MobileActions) -> None:
        self._driver = driver
        self._waiter = waiter
        self._actions = actions
"""

_EXAMPLE_FLOW = """\
\"\"\"Example flow — replace with your own multi-page journeys.\"\"\"


from flows.base_flow import BaseFlow
from pages.example_page import ExamplePage


class ExampleFlow(BaseFlow):
    \"\"\"Orchestrates a simple journey that starts on ExamplePage.

    Replace ExamplePage with real page imports and add business-logic steps
    that span multiple screens of your app.
    \"\"\"

    def _example_page(self) -> ExamplePage:
        return ExamplePage(self._driver, self._waiter, self._actions)

    def open_example(self) -> ExamplePage:
        \"\"\"Navigate to ExamplePage and confirm it loads.\"\"\"
        page = self._example_page()
        assert page.is_loaded(), "ExamplePage did not load"
        return page
"""

_SMOKE_TEST = """\
\"\"\"Starter smoke test — adapt to your app.\"\"\"

import pytest


@pytest.mark.smoke
def test_app_launches(driver) -> None:
    \"\"\"Verify the app opens and a session can be established.\"\"\"
    assert driver is not None, "Driver should be created"
"""

_GITIGNORE_EXTRA = """\
# appium-pytest-kit artifacts
artifacts/
.env
"""


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for `appium-pytest-kit-init`."""

    parser = argparse.ArgumentParser(description="Create a starter .env for appium-pytest-kit")
    parser.add_argument(
        "--path",
        default=".env",
        help="Output path for the generated env template (default: .env)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file when it already exists",
    )
    parser.add_argument(
        "--framework",
        action="store_true",
        help=(
            "Scaffold a full project structure: pages/, flows/, tests/android/, "
            "tests/ios/, data/devices.yaml, conftest.py, pytest.ini"
        ),
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory for the framework scaffold (default: current directory)",
    )
    return parser


def init_env_file(path: Path, *, force: bool = False) -> bool:
    """Create a starter env file. Returns True when written."""

    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ENV_TEMPLATE, encoding="utf-8")
    return True


def scaffold_framework(root: Path, *, force: bool = False) -> list[str]:
    """Generate a full framework scaffold under *root*. Returns list of created paths."""

    created: list[str] = []

    def _write(rel: str, content: str) -> None:
        dest = root / rel
        if dest.exists() and not force:
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        created.append(str(dest))

    _write("data/devices.yaml", _DEVICES_YAML)
    _write("pages/__init__.py", "")
    _write("pages/base_page.py", _BASE_PAGE)
    _write("pages/example_page.py", _EXAMPLE_PAGE)
    _write("flows/__init__.py", "")
    _write("flows/base_flow.py", _BASE_FLOW)
    _write("flows/example_flow.py", _EXAMPLE_FLOW)
    _write("tests/__init__.py", "")
    _write("tests/android/__init__.py", "")
    _write("tests/android/test_smoke.py", _SMOKE_TEST)
    _write("tests/ios/__init__.py", "")
    _write("tests/ios/test_smoke.py", _SMOKE_TEST)
    _write("conftest.py", _CONFTEST_PY)
    _write("pytest.ini", _PYTEST_INI)
    _write(".env", ENV_TEMPLATE)
    _write(".env.example", ENV_TEMPLATE)
    _write(".gitignore", _GITIGNORE_EXTRA)

    return created


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point used by `appium-pytest-kit-init`."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.framework:
        root = Path(args.root).resolve()
        created = scaffold_framework(root, force=args.force)
        if created:
            print(f"Scaffolded framework in {root}:")
            for path in created:
                print(f"  {path}")
        else:
            print(f"Nothing to scaffold in {root} (use --force to overwrite existing files).")
        return 0

    output_path = Path(args.path)
    written = init_env_file(output_path, force=args.force)

    if written:
        print(f"Created {output_path}")
        return 0

    print(f"Skipped {output_path} (already exists). Use --force to overwrite.")
    return 0
