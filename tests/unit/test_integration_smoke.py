"""Integration smoke tests — validate the happy-path fixture chain with a mocked driver.

These tests exercise the full settings → driver config → driver → waiter → actions
pipeline without requiring a real Appium server.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from appium_pytest_kit import pytest_plugin
from appium_pytest_kit._internal.device_resolver import DeviceInfo
from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.driver import DriverConfig, build_driver_config
from appium_pytest_kit.settings import AppiumPytestKitSettings
from appium_pytest_kit.waits import Waiter


@pytest.fixture()
def minimal_settings(monkeypatch, tmp_path):
    """Create minimal valid settings without touching real env."""
    monkeypatch.delenv("APP_PLATFORM", raising=False)
    monkeypatch.delenv("APP_APPIUM_URL", raising=False)
    monkeypatch.delenv("APP_APP_PACKAGE", raising=False)
    monkeypatch.delenv("APP_APP_ACTIVITY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "APP_PLATFORM=android\n"
        "APP_APPIUM_URL=http://127.0.0.1:4723\n"
        "APP_APP_PACKAGE=com.example.app\n"
        "APP_APP_ACTIVITY=.MainActivity\n"
    )
    return AppiumPytestKitSettings(_env_file=str(env_file))


@pytest.fixture()
def mock_driver():
    """Return a MagicMock that satisfies the Appium driver interface."""
    driver = MagicMock()
    driver.session_id = "smoke-session-001"
    driver.quit = MagicMock()
    driver.implicitly_wait = MagicMock()
    driver.find_element = MagicMock()
    driver.find_elements = MagicMock(return_value=[])
    type(driver).contexts = PropertyMock(return_value=["NATIVE_APP"])
    type(driver).current_activity = PropertyMock(return_value=".MainActivity")
    type(driver).page_source = PropertyMock(return_value="<hierarchy/>")
    return driver


class TestSettingsToDriverConfig:
    """Verify settings produce a valid DriverConfig."""

    def test_builds_android_capabilities(self, minimal_settings):
        config = build_driver_config(minimal_settings)

        assert config.server_url == "http://127.0.0.1:4723"
        assert config.capabilities["platformName"] == "android"
        assert config.capabilities["automationName"] == "UiAutomator2"
        assert config.capabilities["appPackage"] == "com.example.app"
        assert config.capabilities["appActivity"] == ".MainActivity"
        assert isinstance(config.implicit_wait, float)

    def test_builds_ios_capabilities(self, monkeypatch, tmp_path):
        monkeypatch.delenv("APP_PLATFORM", raising=False)
        monkeypatch.delenv("APP_APPIUM_URL", raising=False)
        monkeypatch.delenv("APP_BUNDLE_ID", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text(
            "APP_PLATFORM=ios\n"
            "APP_APPIUM_URL=http://127.0.0.1:4723\n"
            "APP_BUNDLE_ID=com.example.app\n"
        )
        settings = AppiumPytestKitSettings(_env_file=str(env_file))
        config = build_driver_config(settings)

        assert config.capabilities["platformName"] == "ios"
        assert config.capabilities["automationName"] == "XCUITest"
        assert config.capabilities["bundleId"] == "com.example.app"

    def test_device_info_merges_into_capabilities(self, minimal_settings):
        config = build_driver_config(minimal_settings)
        capabilities = dict(config.capabilities)
        info = DeviceInfo(
            device_name="Pixel 8",
            platform_name="android",
            udid="emulator-5554",
            platform_version="14",
        )
        pytest_plugin._apply_device_info(capabilities, info)

        assert capabilities["deviceName"] == "Pixel 8"
        assert capabilities["udid"] == "emulator-5554"
        assert capabilities["platformVersion"] == "14"


class TestDriverToWaiterToActions:
    """Verify the driver → waiter → actions chain works with a mock driver."""

    def test_waiter_wraps_driver_with_timeout(self, mock_driver, minimal_settings):
        waiter = Waiter(mock_driver, default_timeout=minimal_settings.explicit_wait_timeout)

        assert waiter.default_timeout == minimal_settings.explicit_wait_timeout
        assert waiter._driver is mock_driver

    def test_actions_wraps_driver_and_waiter(self, mock_driver, minimal_settings):
        waiter = Waiter(mock_driver, default_timeout=minimal_settings.explicit_wait_timeout)
        actions = MobileActions(mock_driver, waiter)

        assert actions._driver is mock_driver
        assert actions._waiter is waiter

    def test_actions_tap_delegates_to_driver(self, mock_driver, minimal_settings):
        element = MagicMock()
        mock_driver.find_element.return_value = element

        waiter = Waiter(mock_driver, default_timeout=5.0)
        actions = MobileActions(mock_driver, waiter)

        with patch.object(waiter, "for_visibility", return_value=element):
            actions.tap(("id", "submit_button"))

        element.click.assert_called_once()

    def test_actions_type_text_delegates_to_driver(self, mock_driver, minimal_settings):
        element = MagicMock()

        waiter = Waiter(mock_driver, default_timeout=5.0)
        actions = MobileActions(mock_driver, waiter)

        with patch.object(waiter, "for_visibility", return_value=element):
            actions.type_text(("id", "username_field"), "testuser")

        element.send_keys.assert_called_once_with("testuser")

    def test_actions_assert_displayed(self, mock_driver):
        element = MagicMock()
        element.is_displayed.return_value = True

        waiter = Waiter(mock_driver, default_timeout=5.0)
        actions = MobileActions(mock_driver, waiter)

        with patch.object(waiter, "for_visibility", return_value=element):
            actions.assert_displayed(("id", "welcome_banner"))


class TestFullFixtureChain:
    """End-to-end chain: settings → config → mocked driver → waiter → actions."""

    def test_happy_path_android(self, minimal_settings, mock_driver, monkeypatch):
        config = build_driver_config(minimal_settings)

        assert config.capabilities["platformName"] == "android"
        assert config.capabilities["automationName"] == "UiAutomator2"

        monkeypatch.setattr(
            "appium_pytest_kit.driver.webdriver.Remote",
            MagicMock(return_value=mock_driver),
        )

        from appium_pytest_kit.driver import create_driver

        driver = create_driver(config)

        assert driver.session_id == "smoke-session-001"

        waiter = Waiter(driver, default_timeout=minimal_settings.explicit_wait_timeout)
        actions = MobileActions(driver, waiter)

        element = MagicMock()
        element.text = "Welcome"
        element.is_displayed.return_value = True

        with patch.object(waiter, "for_visibility", return_value=element):
            actions.tap(("id", "login_button"))
            actions.assert_displayed(("id", "login_button"))
            assert actions.is_displayed(("id", "login_button"))

        element.click.assert_called_once()

        driver.quit()
        driver.quit.assert_called_once()

    def test_driver_config_round_trips_through_frozen_dataclass(self, minimal_settings):
        config = build_driver_config(minimal_settings)

        assert isinstance(config, DriverConfig)
        assert config.server_url == minimal_settings.appium_url
        assert "platformName" in config.capabilities

        with pytest.raises(AttributeError):
            config.server_url = "http://other:4723"
