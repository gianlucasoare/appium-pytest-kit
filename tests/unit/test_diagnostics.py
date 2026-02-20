"""Tests for artifact capture helpers."""

from pathlib import Path
from unittest.mock import MagicMock
import subprocess

from appium_pytest_kit._internal.diagnostics import (
    _safe_filename,
    capture_device_logs,
    capture_page_source,
    capture_screenshot,
)


class TestSafeFilename:
    def test_replaces_colons_and_slashes(self) -> None:
        result = _safe_filename("tests/unit/test_foo.py::TestClass::test_method")
        assert "::" not in result
        assert "/" not in result

    def test_only_safe_characters(self) -> None:
        result = _safe_filename("path/to::test[param]")
        for ch in result:
            assert ch.isalnum() or ch in ("-", "_"), f"Unsafe char: {ch!r}"


class TestCaptureScreenshot:
    def test_saves_screenshot_and_returns_path(self, tmp_path: Path) -> None:
        driver = MagicMock()
        driver.save_screenshot = MagicMock()

        result = capture_screenshot(driver, "test_foo::bar", tmp_path)

        assert result is not None
        assert result.suffix == ".png"
        assert result.parent.name == "screenshots"
        driver.save_screenshot.assert_called_once_with(str(result))

    def test_returns_none_on_driver_exception(self, tmp_path: Path) -> None:
        driver = MagicMock()
        driver.save_screenshot.side_effect = Exception("driver gone")

        result = capture_screenshot(driver, "test_foo", tmp_path)

        assert result is None


class TestCapturePageSource:
    def test_saves_page_source_and_returns_path(self, tmp_path: Path) -> None:
        driver = MagicMock()
        driver.page_source = "<xml><root/></xml>"

        result = capture_page_source(driver, "test_foo::bar", tmp_path)

        assert result is not None
        assert result.suffix == ".xml"
        assert result.parent.name == "pagesource"
        assert result.read_text(encoding="utf-8") == "<xml><root/></xml>"

    def test_returns_none_on_driver_exception(self, tmp_path: Path) -> None:
        driver = MagicMock()
        def _raise(_self):
            raise RuntimeError("driver gone")

        type(driver).page_source = property(fget=_raise)

        result = capture_page_source(driver, "test_foo", tmp_path)

        assert result is None


class TestCaptureDeviceLogs:
    def test_android_logs_saved(self, tmp_path: Path, monkeypatch) -> None:
        driver = MagicMock()
        driver.capabilities = {"platformName": "android", "udid": "emulator-5554"}

        def _fake_run(cmd, **kwargs):
            assert cmd[:3] == ["adb", "-s", "emulator-5554"]
            return subprocess.CompletedProcess(cmd, 0, stdout="log line", stderr="")

        monkeypatch.setattr("appium_pytest_kit._internal.diagnostics.subprocess.run", _fake_run)
        result = capture_device_logs(driver, "test_foo::bar", tmp_path, platform="android")

        assert result is not None
        assert result.parent.name == "device_logs"
        assert "log line" in result.read_text(encoding="utf-8")

    def test_ios_simulator_logs_saved(self, tmp_path: Path, monkeypatch) -> None:
        driver = MagicMock()
        driver.capabilities = {"platformName": "ios", "udid": "SIM-123"}

        def _fake_run(cmd, **kwargs):
            assert cmd[:3] == ["xcrun", "simctl", "spawn"]
            return subprocess.CompletedProcess(cmd, 0, stdout="ios log", stderr="")

        monkeypatch.setattr("appium_pytest_kit._internal.diagnostics.subprocess.run", _fake_run)
        result = capture_device_logs(
            driver,
            "test_ios::fails",
            tmp_path,
            platform="ios",
            udid="SIM-123",
            is_simulator=True,
        )

        assert result is not None
        assert "ios log" in result.read_text(encoding="utf-8")

    def test_returns_none_when_command_not_found(self, tmp_path: Path, monkeypatch) -> None:
        driver = MagicMock()
        driver.capabilities = {"platformName": "android"}

        def _missing(*_args, **_kwargs):
            raise FileNotFoundError()

        monkeypatch.setattr("appium_pytest_kit._internal.diagnostics.subprocess.run", _missing)
        result = capture_device_logs(driver, "test_missing::logs", tmp_path, platform="android")
        assert result is None
