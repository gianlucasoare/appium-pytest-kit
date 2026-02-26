"""Tests for DeviceResolver and validate_launch_config."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from appium_pytest_kit._internal.device_resolver import (
    DeviceInfo,
    DeviceResolver,
    validate_launch_config,
)
from appium_pytest_kit.errors import ConfigurationError, LaunchValidationError
from appium_pytest_kit.settings import AppiumPytestKitSettings


def _settings(**kwargs) -> AppiumPytestKitSettings:
    base = {
        "APP_PLATFORM": "android",
        "APP_APPIUM_URL": "http://127.0.0.1:4723",
    }
    for k, v in kwargs.items():
        base[k.upper() if not k.startswith("APP_") else k] = v
    return AppiumPytestKitSettings(**{k.lower().removeprefix("app_"): v for k, v in base.items()})


def _make_settings(**kwargs) -> AppiumPytestKitSettings:
    """Create settings from keyword args matching field names."""
    return AppiumPytestKitSettings.model_validate(
        {
            "platform": "android",
            "appium_url": "http://127.0.0.1:4723",
            **kwargs,
        }
    )


class TestDeviceInfo:
    def test_dataclass_is_frozen(self) -> None:
        info = DeviceInfo(device_name="Pixel 7", platform_name="android")
        with pytest.raises((AttributeError, TypeError)):
            info.device_name = "other"  # type: ignore[misc]

    def test_optional_fields_default_to_none(self) -> None:
        info = DeviceInfo(device_name="Test", platform_name="ios")
        assert info.udid is None
        assert info.platform_version is None
        assert info.automation_name is None
        assert info.is_simulator is False


class TestTier1Explicit:
    def test_explicit_device_name_resolved(self) -> None:
        s = _make_settings(device_name="My Phone", platform="android")
        info = DeviceResolver(s).resolve()
        assert info is not None
        assert info.device_name == "My Phone"
        assert info.platform_name == "android"

    def test_explicit_udid_resolved(self) -> None:
        s = _make_settings(udid="UDID123")
        info = DeviceResolver(s).resolve()
        assert info is not None
        assert info.udid == "UDID123"

    def test_is_simulator_propagated(self) -> None:
        s = _make_settings(device_name="Sim", is_simulator=True)
        info = DeviceResolver(s).resolve()
        assert info is not None
        assert info.is_simulator is True


class TestTier2Yaml:
    def test_yaml_profile_loaded(self, tmp_path: Path) -> None:
        yaml_content = (
            "devices:\n"
            "  pixel7:\n"
            "    device_name: Pixel 7\n"
            "    platform: android\n"
            "    platform_version: '14'\n"
            "    is_simulator: false\n"
        )
        devices_file = tmp_path / "devices.yaml"
        devices_file.write_text(yaml_content, encoding="utf-8")

        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        s = _make_settings(device_profile="pixel7", devices_yaml=devices_file)
        info = DeviceResolver(s).resolve()
        assert info is not None
        assert info.device_name == "Pixel 7"
        assert info.platform_version == "14"

    def test_yaml_missing_profile_raises_config_error(self, tmp_path: Path) -> None:
        yaml_content = "devices:\n  other:\n    device_name: Other\n"
        devices_file = tmp_path / "devices.yaml"
        devices_file.write_text(yaml_content, encoding="utf-8")

        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        s = _make_settings(device_profile="nonexistent", devices_yaml=devices_file)
        with pytest.raises(ConfigurationError, match="nonexistent"):
            DeviceResolver(s).resolve()

    def test_yaml_missing_file_raises_config_error(self, tmp_path: Path) -> None:
        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        s = _make_settings(
            device_profile="pixel7",
            devices_yaml=tmp_path / "missing.yaml",
        )
        with pytest.raises(ConfigurationError, match="not found"):
            DeviceResolver(s).resolve()


class TestTier3AutoDetect:
    def test_adb_not_found_returns_none(self) -> None:
        s = _make_settings(platform="android")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            info = DeviceResolver(s).resolve()
        assert info is None

    def test_adb_timeout_returns_none(self) -> None:
        import subprocess

        s = _make_settings(platform="android")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("adb", 10)):
            info = DeviceResolver(s).resolve()
        assert info is None

    def test_adb_no_devices_returns_none(self) -> None:
        s = _make_settings(platform="android")
        mock_result = MagicMock()
        mock_result.stdout = "List of devices attached\n\n"
        with patch("subprocess.run", return_value=mock_result):
            info = DeviceResolver(s).resolve()
        assert info is None

    def test_adb_device_found(self) -> None:
        s = _make_settings(platform="android")
        adb_devices_output = "List of devices attached\nABC123 device product:pixel model:Pixel_7\n"
        model_output = "Pixel 7"
        version_output = "14"

        call_count = 0

        def fake_run(cmd, **kwargs):
            nonlocal call_count
            call_count += 1
            result = MagicMock()
            if "devices" in cmd:
                result.stdout = adb_devices_output
            elif "ro.product.model" in cmd:
                result.stdout = model_output
            else:
                result.stdout = version_output
            return result

        with patch("subprocess.run", side_effect=fake_run):
            info = DeviceResolver(s).resolve()

        assert info is not None
        assert info.udid == "ABC123"
        assert info.platform_name == "android"

    def test_ios_device_detection_skips_host_mac(self) -> None:
        s = _make_settings(platform="ios")
        output = (
            "== Devices ==\n"
            "My Mac (14.5) (11111111-2222-3333-4444-555555555555)\n"
            "iPhone 15 Pro (17.4) (AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE)\n"
        )
        result = MagicMock()
        result.stdout = output
        with patch("subprocess.run", return_value=result):
            info = DeviceResolver(s).resolve()

        assert info is not None
        assert info.device_name == "iPhone 15 Pro"
        assert info.udid == "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE"
        assert info.platform_name == "ios"


class TestLaunchValidation:
    def test_android_with_app_passes(self) -> None:
        s = _make_settings(platform="android", app="/path/app.apk")
        validate_launch_config(s)  # should not raise

    def test_android_with_package_and_activity_passes(self) -> None:
        s = _make_settings(
            platform="android",
            app_package="com.example",
            app_activity=".MainActivity",
        )
        validate_launch_config(s)

    def test_android_without_app_info_raises(self) -> None:
        s = _make_settings(platform="android")
        with pytest.raises(LaunchValidationError):
            validate_launch_config(s)

    def test_android_with_blank_app_values_raises(self) -> None:
        s = _make_settings(platform="android", app="", app_package="", app_activity="")
        with pytest.raises(LaunchValidationError):
            validate_launch_config(s)

    def test_android_with_auto_discovered_app_passes(self, tmp_path: Path) -> None:
        builds = tmp_path / "app_builds" / "android"
        builds.mkdir(parents=True)
        (builds / "demo.apk").write_bytes(b"apk")

        s = _make_settings(
            platform="android",
            app_auto_discover=True,
            app_builds_dir=tmp_path / "app_builds",
        )
        validate_launch_config(s)

    def test_ios_with_app_passes(self) -> None:
        s = _make_settings(platform="ios", app="/path/app.ipa")
        validate_launch_config(s)

    def test_ios_with_bundle_id_passes(self) -> None:
        s = _make_settings(platform="ios", bundle_id="com.example.app")
        validate_launch_config(s)

    def test_ios_without_app_info_raises(self) -> None:
        s = _make_settings(platform="ios")
        with pytest.raises(LaunchValidationError):
            validate_launch_config(s)

    def test_ios_with_auto_discovered_app_passes(self, tmp_path: Path) -> None:
        builds = tmp_path / "app_builds" / "ios" / "device"
        builds.mkdir(parents=True)
        (builds / "demo.ipa").write_bytes(b"ipa")

        s = _make_settings(
            platform="ios",
            app_auto_discover=True,
            app_builds_dir=tmp_path / "app_builds",
        )
        validate_launch_config(s)
