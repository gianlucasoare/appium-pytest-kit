
from collections.abc import Mapping
import os
from pathlib import Path
from typing import Any

from appium_pytest_kit.driver import build_driver_config, discover_latest_app_build
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


def test_auto_discover_android_picks_latest_build(tmp_path: Path) -> None:
    builds = tmp_path / "app_builds" / "android"
    builds.mkdir(parents=True)
    older = builds / "app-old.apk"
    newer = builds / "app-new.apk"
    older.write_bytes(b"old")
    newer.write_bytes(b"new")
    os.utime(older, (older.stat().st_atime, older.stat().st_mtime - 20))

    settings = AppiumPytestKitSettings(
        platform="android",
        app_auto_discover=True,
        app_builds_dir=tmp_path / "app_builds",
    )

    discovered = discover_latest_app_build(settings)
    assert discovered == str(newer)

    config = build_driver_config(settings)
    assert config.capabilities["app"] == str(newer)


def test_auto_discover_ios_simulator_prefers_app_bundle(tmp_path: Path) -> None:
    sim_dir = tmp_path / "app_builds" / "ios" / "simulator"
    sim_dir.mkdir(parents=True)
    app_bundle = sim_dir / "Demo.app"
    app_bundle.mkdir()

    settings = AppiumPytestKitSettings(
        platform="ios",
        is_simulator=True,
        app_auto_discover=True,
        app_builds_dir=tmp_path / "app_builds",
    )

    discovered = discover_latest_app_build(settings)
    assert discovered == str(app_bundle)
