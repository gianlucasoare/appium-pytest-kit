"""appium-pytest-kit public package API."""

from appium_pytest_kit._internal.device_resolver import DeviceInfo
from appium_pytest_kit._version import __version__
from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.api import ApiClient, ApiResponse
from appium_pytest_kit.driver import DriverConfig, build_driver_config, create_driver
from appium_pytest_kit.errors import (
    ActionError,
    ApiRequestError,
    AppiumPytestKitError,
    ConfigurationError,
    DeviceResolutionError,
    DriverCreationError,
    LaunchValidationError,
    WaitTimeoutError,
)
from appium_pytest_kit.parametrize import cross_platform, from_file, load_test_data
from appium_pytest_kit.settings import AppiumPytestKitSettings, apply_cli_overrides, load_settings
from appium_pytest_kit.visual import (
    BaselineManager,
    ScreenshotDiff,
    VisualRegressionError,
    assert_screenshot_match,
    compare_screenshots,
)
from appium_pytest_kit.waits import Locator, Waiter

__all__ = [
    "ActionError",
    "ApiClient",
    "ApiRequestError",
    "ApiResponse",
    "AppiumPytestKitError",
    "AppiumPytestKitSettings",
    "BaselineManager",
    "ConfigurationError",
    "DeviceInfo",
    "DeviceResolutionError",
    "DriverConfig",
    "DriverCreationError",
    "LaunchValidationError",
    "Locator",
    "MobileActions",
    "ScreenshotDiff",
    "VisualRegressionError",
    "WaitTimeoutError",
    "Waiter",
    "__version__",
    "apply_cli_overrides",
    "assert_screenshot_match",
    "build_driver_config",
    "compare_screenshots",
    "create_driver",
    "cross_platform",
    "from_file",
    "load_settings",
    "load_test_data",
]
