"""Command-line utilities for appium-pytest-kit."""


import argparse
from collections.abc import Sequence
from pathlib import Path

ENV_TEMPLATE = """# appium-pytest-kit starter configuration
# Copy this file to your project root and adjust values.

APP_PLATFORM=android
APP_APPIUM_URL=http://127.0.0.1:4723
APP_MANAGE_APPIUM_SERVER=false
APP_DEVICE_NAME=
APP_PLATFORM_VERSION=
APP_UDID=
APP_APP=
APP_APPIUM_BASE_PATH=/
APP_CAPABILITIES_JSON={}
APP_SESSION_MODE=clean
APP_VIDEO_POLICY=never
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
    _write("tests/__init__.py", "")
    _write("tests/android/__init__.py", "")
    _write("tests/android/test_smoke.py", _SMOKE_TEST)
    _write("tests/ios/__init__.py", "")
    _write("tests/ios/test_smoke.py", _SMOKE_TEST)
    _write("conftest.py", _CONFTEST_PY)
    _write("pytest.ini", _PYTEST_INI)
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
