"""Tests for artifact capture helpers."""

from pathlib import Path
from unittest.mock import MagicMock

from appium_pytest_kit._internal.diagnostics import (
    _safe_filename,
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
