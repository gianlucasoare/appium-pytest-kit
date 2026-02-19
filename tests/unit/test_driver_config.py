from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from appium_pytest_kit.driver import build_driver_config
from appium_pytest_kit.interfaces import CapabilitiesAdapter
from appium_pytest_kit.settings import AppiumPytestKitSettings


class LocaleCapabilitiesAdapter(CapabilitiesAdapter):
    def adapt(
        self,
        capabilities: Mapping[str, Any],
        settings: AppiumPytestKitSettings,
    ) -> Mapping[str, Any]:
        _ = settings
        payload = dict(capabilities)
        payload["language"] = "en"
        return payload


def test_build_driver_config_android_defaults() -> None:
    settings = AppiumPytestKitSettings(
        platform="android",
        app_package="com.example.app",
        app_activity=".MainActivity",
    )

    config = build_driver_config(settings)

    assert config.server_url == settings.appium_url
    assert config.capabilities["platformName"] == "android"
    assert config.capabilities["automationName"] == "UiAutomator2"
    assert config.capabilities["appPackage"] == "com.example.app"
    assert config.capabilities["appActivity"] == ".MainActivity"


def test_build_driver_config_ios_with_adapter() -> None:
    settings = AppiumPytestKitSettings(
        platform="ios",
        bundle_id="com.example.ios",
        capabilities_json={"autoAcceptAlerts": True},
    )

    config = build_driver_config(settings, adapters=[LocaleCapabilitiesAdapter()])

    assert config.capabilities["platformName"] == "ios"
    assert config.capabilities["automationName"] == "XCUITest"
    assert config.capabilities["bundleId"] == "com.example.ios"
    assert config.capabilities["autoAcceptAlerts"] is True
    assert config.capabilities["language"] == "en"
