"""Driver configuration and construction utilities."""


from collections.abc import Iterable
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any

from appium import webdriver
from appium.options.common import AppiumOptions

from appium_pytest_kit.errors import DriverCreationError
from appium_pytest_kit.interfaces import CapabilitiesAdapter
from appium_pytest_kit.settings import AppiumPytestKitSettings

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DriverConfig:
    """Runtime driver connection details."""

    server_url: str
    capabilities: dict[str, Any]
    implicit_wait: float


def _default_automation_name(platform: str) -> str:
    return "UiAutomator2" if platform == "android" else "XCUITest"


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def _candidate_app_paths(settings: AppiumPytestKitSettings) -> list[Path]:
    base_dir = Path(settings.app_builds_dir)
    if not base_dir.exists():
        return []

    def _collect(roots: list[Path], suffixes: set[str], *, allow_dirs: bool = False) -> list[Path]:
        discovered: list[Path] = []
        visited: set[Path] = set()
        for root in roots:
            if not root.exists() or root in visited:
                continue
            visited.add(root)
            for candidate in root.rglob("*"):
                suffix = candidate.suffix.lower()
                if suffix not in suffixes:
                    continue
                if candidate.is_file() or (allow_dirs and candidate.is_dir()):
                    discovered.append(candidate)
        return discovered

    if settings.platform == "android":
        return _collect(
            [base_dir / "android", base_dir],
            {".apk", ".aab"},
        )

    ios_root = base_dir / "ios"
    if settings.is_simulator:
        primary = _collect(
            [ios_root / "simulator", ios_root, base_dir],
            {".app"},
            allow_dirs=True,
        )
        fallback = _collect(
            [ios_root / "simulator", ios_root, base_dir],
            {".ipa"},
        )
        return [*primary, *fallback]

    primary = _collect(
        [ios_root / "device", ios_root, base_dir],
        {".ipa"},
    )
    fallback = _collect(
        [ios_root / "device", ios_root, base_dir],
        {".app"},
        allow_dirs=True,
    )
    return [*primary, *fallback]


def discover_latest_app_build(settings: AppiumPytestKitSettings) -> str | None:
    """Return latest app binary path from app_builds/* when auto-discovery is enabled."""

    if not settings.app_auto_discover:
        return None

    candidates = _candidate_app_paths(settings)
    if not candidates:
        logger.info(
            "app:auto-discovery enabled but no candidate build found under %s",
            settings.app_builds_dir,
        )
        return None

    def _sort_key(path: Path) -> tuple[float, str]:
        try:
            modified = path.stat().st_mtime
        except OSError:
            modified = -1.0
        return modified, str(path)

    latest = max(candidates, key=_sort_key)
    logger.info("app:auto-discovered build=%s", latest)
    return str(latest)


def _base_capabilities(settings: AppiumPytestKitSettings) -> dict[str, Any]:
    resolved_app = settings.app if _has_value(settings.app) else discover_latest_app_build(settings)

    caps: dict[str, Any] = {
        "platformName": settings.platform,
        "automationName": settings.automation_name
        or _default_automation_name(settings.platform),
        "newCommandTimeout": settings.new_command_timeout,
        "noReset": settings.no_reset,
        "fullReset": settings.full_reset,
    }

    optional_shared = {
        "deviceName": settings.device_name,
        "platformVersion": settings.platform_version,
        "udid": settings.udid,
        "app": resolved_app,
    }
    caps.update({key: value for key, value in optional_shared.items() if _has_value(value)})

    if settings.platform == "android":
        optional_android = {
            "appPackage": settings.app_package,
            "appActivity": settings.app_activity,
        }
        caps.update({key: value for key, value in optional_android.items() if _has_value(value)})
    if settings.platform == "ios" and _has_value(settings.bundle_id):
        caps["bundleId"] = settings.bundle_id

    caps.update(settings.capabilities_json)
    return caps


def build_driver_config(
    settings: AppiumPytestKitSettings,
    *,
    server_url: str | None = None,
    adapters: Iterable[CapabilitiesAdapter] = (),
) -> DriverConfig:
    """Build a driver config from settings and capability adapters."""

    capabilities = _base_capabilities(settings)
    for adapter in adapters:
        capabilities = dict(adapter.adapt(capabilities, settings))

    return DriverConfig(
        server_url=server_url or settings.appium_url,
        capabilities=capabilities,
        implicit_wait=settings.implicit_wait,
    )


def create_driver(config: DriverConfig):
    """Create an Appium WebDriver from a driver config."""

    options = AppiumOptions()
    options.load_capabilities(config.capabilities)

    try:
        driver = webdriver.Remote(command_executor=config.server_url, options=options)
    except Exception as exc:  # pragma: no cover - integration boundary
        message = f"Failed to create Appium session at {config.server_url}"
        raise DriverCreationError(message) from exc

    if config.implicit_wait > 0:
        driver.implicitly_wait(config.implicit_wait)
    return driver
