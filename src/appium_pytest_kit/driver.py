"""Driver configuration and construction utilities."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from appium import webdriver
from appium.options.common import AppiumOptions

from appium_pytest_kit.errors import DriverCreationError
from appium_pytest_kit.interfaces import CapabilitiesAdapter
from appium_pytest_kit.settings import AppiumPytestKitSettings


@dataclass(frozen=True, slots=True)
class DriverConfig:
    """Runtime driver connection details."""

    server_url: str
    capabilities: dict[str, Any]
    implicit_wait: float


def _default_automation_name(platform: str) -> str:
    return "UiAutomator2" if platform == "android" else "XCUITest"


def _base_capabilities(settings: AppiumPytestKitSettings) -> dict[str, Any]:
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
        "app": settings.app,
    }
    caps.update({key: value for key, value in optional_shared.items() if value is not None})

    if settings.platform == "android":
        optional_android = {
            "appPackage": settings.app_package,
            "appActivity": settings.app_activity,
        }
        caps.update({key: value for key, value in optional_android.items() if value is not None})
    if settings.platform == "ios" and settings.bundle_id is not None:
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
