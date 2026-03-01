"""Command-line utilities for appium-pytest-kit."""


import argparse
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import urlopen

from appium_pytest_kit._internal.device_resolver import validate_launch_config
from appium_pytest_kit.errors import LaunchValidationError
from appium_pytest_kit.settings import AppiumPytestKitSettings, load_settings

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

# Strict config mode:
#   false - unknown --app-override keys become capability overrides (default)
#   true  - unknown --app-override keys fail fast; unknown capability keys fail validation
APP_STRICT_CONFIG=false

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
from appium_pytest_kit.api import ApiClient
from appium_pytest_kit.settings import AppiumPytestKitSettings


@pytest.fixture(scope="session")
def app_settings(settings: AppiumPytestKitSettings) -> AppiumPytestKitSettings:
    \"\"\"Expose settings to tests under a shorter alias.\"\"\"
    return settings


@pytest.fixture(scope="session")
def api_client() -> ApiClient:
    \"\"\"Provide a shared API client for endpoint tests.\"\"\"
    from api.client import get_api_client

    return get_api_client()
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
    api: backend API endpoint tests
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

_API_CLIENT = """\
\"\"\"API client factory used by tests/api/*.py.\"\"\"

import os

from appium_pytest_kit.api import ApiClient


def get_api_client() -> ApiClient:
    \"\"\"Create an ApiClient from environment variables.\"\"\"
    base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    token = os.getenv("API_TOKEN")

    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return ApiClient(base_url=base_url, default_headers=headers, timeout=20.0)
"""

_API_HEALTH_TEST = """\
\"\"\"Starter API test — adapt endpoint and assertions to your backend.\"\"\"

import pytest


@pytest.mark.api
def test_health_endpoint(api_client) -> None:
    \"\"\"Sanity-check a health endpoint and expect 2xx response.\"\"\"
    response = api_client.get("/health", expected_status=range(200, 300))
    assert response.status_code in range(200, 300)
"""

_GITIGNORE_EXTRA = """\
# appium-pytest-kit artifacts
artifacts/
.env
"""

_ALLOWED_EXTRAS: tuple[str, ...] = ("all", "allure", "dev", "retry", "xdist", "yaml")


@dataclass(slots=True)
class DoctorCheck:
    """Single doctor check result row."""

    name: str
    status: str
    details: str


def _status_endpoint(server_url: str) -> str:
    parsed = urlparse(server_url)
    base_path = parsed.path.rstrip("/")
    path = f"{base_path}/status" if base_path else "/status"
    return urlunparse(parsed._replace(path=path, params="", query="", fragment=""))


def _run_command(
    command: Sequence[str],
    *,
    timeout: float = 8.0,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _render_command_output(process: subprocess.CompletedProcess[str]) -> str:
    output = (process.stdout or "").strip() or (process.stderr or "").strip()
    if not output:
        return "no output"
    first = output.splitlines()[0].strip()
    return first or "no output"


def _tool_check(name: str, command: Sequence[str], *, timeout: float = 8.0) -> DoctorCheck:
    try:
        process = _run_command(command, timeout=timeout)
    except FileNotFoundError:
        return DoctorCheck(name=name, status="fail", details=f"{command[0]} not found on PATH")
    except subprocess.TimeoutExpired:
        return DoctorCheck(name=name, status="fail", details=f"{command[0]} check timed out")

    if process.returncode != 0:
        return DoctorCheck(
            name=name,
            status="fail",
            details=f"command failed ({process.returncode}): {_render_command_output(process)}",
        )
    return DoctorCheck(name=name, status="pass", details=_render_command_output(process))


def _parse_driver_names(payload: str) -> list[str]:
    names: set[str] = set()

    try:
        decoded = json.loads(payload)
    except ValueError:
        decoded = None

    if isinstance(decoded, dict):
        installed = decoded.get("installed")
        if isinstance(installed, list):
            for entry in installed:
                if isinstance(entry, str):
                    names.add(entry.lower())
                elif isinstance(entry, dict):
                    raw = entry.get("name") or entry.get("driverName")
                    if raw:
                        names.add(str(raw).lower())
    elif isinstance(decoded, list):
        for entry in decoded:
            if isinstance(entry, str):
                names.add(entry.lower())
            elif isinstance(entry, dict):
                raw = entry.get("name") or entry.get("driverName")
                if raw:
                    names.add(str(raw).lower())

    if not names:
        for match in re.findall(r"(uiautomator2|xcuitest|espresso)", payload, flags=re.IGNORECASE):
            names.add(match.lower())
    return sorted(names)


def _expected_driver(settings: AppiumPytestKitSettings) -> str:
    if settings.platform == "ios":
        return "xcuitest"
    automation = (settings.automation_name or "UiAutomator2").strip().lower()
    if automation == "espresso":
        return "espresso"
    return "uiautomator2"


def _driver_check(settings: AppiumPytestKitSettings, *, timeout: float = 8.0) -> DoctorCheck:
    command = ["appium", "driver", "list", "--installed", "--json"]
    try:
        process = _run_command(command, timeout=timeout)
    except FileNotFoundError:
        return DoctorCheck(
            name="appium drivers",
            status="fail",
            details="appium not found on PATH; cannot inspect installed drivers",
        )
    except subprocess.TimeoutExpired:
        return DoctorCheck(
            name="appium drivers",
            status="warn",
            details="driver list command timed out",
        )

    if process.returncode != 0:
        return DoctorCheck(
            name="appium drivers",
            status="warn",
            details=f"could not list drivers: {_render_command_output(process)}",
        )

    drivers = _parse_driver_names((process.stdout or "").strip())
    expected = _expected_driver(settings)
    if not drivers:
        return DoctorCheck(
            name="appium drivers",
            status="warn",
            details="no installed drivers detected from command output",
        )
    if expected not in drivers:
        return DoctorCheck(
            name="appium drivers",
            status="fail",
            details=(
                f"expected '{expected}' for platform={settings.platform}, "
                f"found: {', '.join(drivers)}"
            ),
        )
    return DoctorCheck(
        name="appium drivers",
        status="pass",
        details=f"{', '.join(drivers)}",
    )


def _server_check(settings: AppiumPytestKitSettings, *, timeout: float = 5.0) -> DoctorCheck:
    if settings.manage_appium_server:
        return DoctorCheck(
            name="appium server",
            status="warn",
            details="APP_MANAGE_APPIUM_SERVER=true (server is started by the test session)",
        )

    status_url = _status_endpoint(settings.appium_url)
    try:
        with urlopen(status_url, timeout=max(timeout, 1.0)) as response:  # nosec B310
            payload = response.read().decode("utf-8", errors="replace")
    except (OSError, URLError) as exc:
        return DoctorCheck(
            name="appium server",
            status="fail",
            details=f"{status_url} unreachable: {exc}",
        )

    try:
        decoded = json.loads(payload)
    except ValueError:
        return DoctorCheck(
            name="appium server",
            status="fail",
            details=f"{status_url} returned invalid JSON",
        )

    value = decoded.get("value") if isinstance(decoded, dict) else None
    if isinstance(value, dict) and value.get("ready") is False:
        return DoctorCheck(name="appium server", status="fail", details=f"{status_url} ready=false")

    return DoctorCheck(name="appium server", status="pass", details=f"{status_url} reachable")


def _launch_config_check(settings: AppiumPytestKitSettings) -> DoctorCheck:
    try:
        validate_launch_config(settings)
        return DoctorCheck(
            name="launch config",
            status="pass",
            details="launch settings look valid",
        )
    except LaunchValidationError as exc:
        return DoctorCheck(name="launch config", status="warn", details=str(exc))


def _artifacts_check(settings: AppiumPytestKitSettings) -> DoctorCheck:
    try:
        settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
        probe = settings.artifacts_dir / ".doctor-write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError as exc:
        return DoctorCheck(
            name="artifacts dir",
            status="warn",
            details=f"{settings.artifacts_dir} is not writable: {exc}",
        )
    return DoctorCheck(
        name="artifacts dir",
        status="pass",
        details=f"{settings.artifacts_dir} writable",
    )


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
            "Scaffold a full project structure: pages/, flows/, api/, tests/android/, "
            "tests/ios/, tests/api/, data/devices.yaml, conftest.py, pytest.ini"
        ),
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory for the framework scaffold (default: current directory)",
    )
    parser.add_argument(
        "--install-extras",
        default=None,
        help=(
            "Install optional extras after scaffolding (only with --framework). "
            "Examples: all | yaml,retry,xdist"
        ),
    )
    return parser


def build_doctor_parser() -> argparse.ArgumentParser:
    """Build CLI parser for `appium-pytest-kit-doctor`."""

    parser = argparse.ArgumentParser(
        description="Run environment and configuration diagnostics for appium-pytest-kit"
    )
    parser.add_argument(
        "--env-file",
        default=None,
        help="Path to env file to validate (default: .env)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout in seconds for server and command probes (default: 5)",
    )
    parser.add_argument(
        "--no-server-check",
        action="store_true",
        help="Skip Appium /status reachability check",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
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
    _write("api/__init__.py", "")
    _write("api/client.py", _API_CLIENT)
    _write("tests/__init__.py", "")
    _write("tests/api/__init__.py", "")
    _write("tests/api/test_health.py", _API_HEALTH_TEST)
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


def _normalize_extras_spec(raw: str) -> str:
    requested = [chunk.strip().lower() for chunk in raw.split(",") if chunk.strip()]
    if not requested:
        msg = (
            "--install-extras requires a value. "
            f"Allowed values: {', '.join(_ALLOWED_EXTRAS)}"
        )
        raise ValueError(msg)

    invalid = sorted({name for name in requested if name not in _ALLOWED_EXTRAS})
    if invalid:
        rendered = ", ".join(repr(name) for name in invalid)
        msg = (
            f"--install-extras got unknown extra(s): {rendered}. "
            f"Allowed values: {', '.join(_ALLOWED_EXTRAS)}"
        )
        raise ValueError(msg)

    deduped: list[str] = []
    seen: set[str] = set()
    for name in requested:
        if name in seen:
            continue
        seen.add(name)
        deduped.append(name)
    return ",".join(deduped)


def install_framework_extras(extras_spec: str) -> None:
    requirement = f"appium-pytest-kit[{extras_spec}]"
    command = [sys.executable, "-m", "pip", "install", requirement]
    subprocess.run(command, check=True)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point used by `appium-pytest-kit-init`."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.install_extras and not args.framework:
        parser.error("--install-extras can only be used with --framework")

    if args.framework:
        root = Path(args.root).resolve()
        created = scaffold_framework(root, force=args.force)
        if created:
            print(f"Scaffolded framework in {root}:")
            for path in created:
                print(f"  {path}")
        else:
            print(f"Nothing to scaffold in {root} (use --force to overwrite existing files).")

        if args.install_extras:
            try:
                normalized_extras = _normalize_extras_spec(args.install_extras)
            except ValueError as exc:
                parser.error(str(exc))

            print(
                f"\nInstalling optional extras ({normalized_extras}) "
                "for appium-pytest-kit in the current Python environment..."
            )
            try:
                install_framework_extras(normalized_extras)
            except subprocess.CalledProcessError as exc:
                print(
                    "Failed to install extras via pip. "
                    f"Command exited with code {exc.returncode}."
                )
                return exc.returncode or 1
            print("Extras installed successfully.")
        return 0

    output_path = Path(args.path)
    written = init_env_file(output_path, force=args.force)

    if written:
        print(f"Created {output_path}")
        return 0

    print(f"Skipped {output_path} (already exists). Use --force to overwrite.")
    return 0


def doctor_main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point used by `appium-pytest-kit-doctor`."""

    parser = build_doctor_parser()
    args = parser.parse_args(argv)

    checks: list[DoctorCheck] = []

    try:
        settings = load_settings(env_file=args.env_file)
        checks.append(DoctorCheck("config load", "pass", "settings loaded successfully"))
    except Exception as exc:
        checks.append(DoctorCheck("config load", "fail", str(exc)))
        settings = None

    checks.append(_tool_check("appium cli", ["appium", "--version"], timeout=args.timeout))

    if settings is not None:
        if settings.platform == "android":
            checks.append(_tool_check("adb", ["adb", "version"], timeout=args.timeout))
        elif settings.platform == "ios":
            checks.append(_tool_check("xcrun", ["xcrun", "--version"], timeout=args.timeout))

        checks.append(_driver_check(settings, timeout=args.timeout))
        checks.append(_launch_config_check(settings))
        checks.append(_artifacts_check(settings))
        if args.no_server_check:
            checks.append(
                DoctorCheck(
                    "appium server",
                    "warn",
                    "server check skipped by --no-server-check",
                )
            )
        else:
            checks.append(_server_check(settings, timeout=args.timeout))

    passed = sum(1 for check in checks if check.status == "pass")
    warned = sum(1 for check in checks if check.status == "warn")
    failed = sum(1 for check in checks if check.status == "fail")

    if args.json:
        payload: dict[str, Any] = {
            "ok": failed == 0,
            "summary": {
                "total": len(checks),
                "passed": passed,
                "warned": warned,
                "failed": failed,
            },
            "checks": [asdict(check) for check in checks],
        }
        print(json.dumps(payload, indent=2))
        return 1 if failed else 0

    for check in checks:
        label = check.status.upper()
        print(f"[{label}] {check.name}: {check.details}")

    print(f"\nSummary: total={len(checks)} passed={passed} warned={warned} failed={failed}")
    return 1 if failed else 0
