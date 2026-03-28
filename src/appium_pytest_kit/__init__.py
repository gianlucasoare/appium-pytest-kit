"""appium-pytest-kit public package API."""

from appium_pytest_kit._internal.device_resolver import DeviceInfo
from appium_pytest_kit._version import __version__
from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.api import ApiClient, ApiResponse
from appium_pytest_kit.cloud import CloudConfig, apply_cloud_config, build_cloud_config
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
from appium_pytest_kit.locator_healing import (
    HealingRegistry,
    HealingResult,
    LocatorChain,
    chain,
)
from appium_pytest_kit.parametrize import cross_platform, from_file, load_test_data
from appium_pytest_kit.settings import AppiumPytestKitSettings, apply_cli_overrides, load_settings
from appium_pytest_kit.soft_assertions import (
    AssertionFailure,
    SoftAssert,
    SoftAssertionError,
    soft_assertions,
)
from appium_pytest_kit.test_data import DataFactory
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
    "AssertionFailure",
    "BaselineManager",
    "CloudConfig",
    "ConfigurationError",
    "DataFactory",
    "DeviceInfo",
    "DeviceResolutionError",
    "DriverConfig",
    "DriverCreationError",
    "HealingRegistry",
    "HealingResult",
    "LaunchValidationError",
    "Locator",
    "LocatorChain",
    "MobileActions",
    "ScreenshotDiff",
    "SoftAssert",
    "SoftAssertionError",
    "VisualRegressionError",
    "WaitTimeoutError",
    "Waiter",
    "__version__",
    "apply_cli_overrides",
    "apply_cloud_config",
    "assert_screenshot_match",
    "build_cloud_config",
    "build_driver_config",
    "chain",
    "compare_screenshots",
    "create_driver",
    "cross_platform",
    "from_file",
    "load_settings",
    "load_test_data",
    "soft_assertions",
]
