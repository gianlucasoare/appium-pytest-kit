"""appium-pytest-kit public package API."""

from appium_pytest_kit._version import __version__
from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.driver import DriverConfig, build_driver_config, create_driver
from appium_pytest_kit.errors import (
    ActionError,
    AppiumPytestKitError,
    ConfigurationError,
    DriverCreationError,
    WaitTimeoutError,
)
from appium_pytest_kit.settings import AppiumPytestKitSettings, apply_cli_overrides, load_settings
from appium_pytest_kit.waits import Waiter

__all__ = [
    "ActionError",
    "AppiumPytestKitError",
    "AppiumPytestKitSettings",
    "ConfigurationError",
    "DriverConfig",
    "DriverCreationError",
    "MobileActions",
    "WaitTimeoutError",
    "Waiter",
    "__version__",
    "apply_cli_overrides",
    "build_driver_config",
    "create_driver",
    "load_settings",
]
