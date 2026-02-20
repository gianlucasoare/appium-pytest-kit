"""Tests for waits added in the second pass (for_all_gone, context, Android)."""

from unittest.mock import MagicMock, patch

import pytest

from appium_pytest_kit.errors import WaitTimeoutError
from appium_pytest_kit.waits import Waiter


def _make_waiter(driver=None, timeout: float = 0.1) -> Waiter:
    driver = driver or MagicMock()
    return Waiter(driver, default_timeout=timeout, poll_frequency=0.05)


class TestForAllGone:
    def test_returns_true_when_all_invisible(self) -> None:
        waiter = _make_waiter()
        locators = [("id", "a"), ("id", "b")]
        with patch(
            "selenium.webdriver.support.expected_conditions.invisibility_of_element_located",
            return_value=lambda d: True,
        ):
            result = waiter.for_all_gone(locators)
        assert result is True

    def test_raises_when_one_still_visible(self) -> None:
        waiter = _make_waiter()
        locators = [("id", "a"), ("id", "b")]
        def _make_cond(locator):
            def _cond(driver):
                return locator != ("id", "b")
            return _cond

        with patch(
            "selenium.webdriver.support.expected_conditions.invisibility_of_element_located",
            side_effect=_make_cond,
        ):
            with pytest.raises(WaitTimeoutError):
                waiter.for_all_gone(locators)

    def test_accepts_generator(self) -> None:
        waiter = _make_waiter()

        def _gen():
            yield ("id", "x")

        with patch(
            "selenium.webdriver.support.expected_conditions.invisibility_of_element_located",
            return_value=lambda d: True,
        ):
            result = waiter.for_all_gone(_gen())
        assert result is True


class TestForContextContains:
    def test_returns_matching_context(self) -> None:
        mock_driver = MagicMock()
        mock_driver.contexts = ["NATIVE_APP", "WEBVIEW_com.example"]
        waiter = _make_waiter(driver=mock_driver)
        result = waiter.for_context_contains("WEBVIEW")
        assert result == "WEBVIEW_com.example"

    def test_raises_when_context_not_found(self) -> None:
        mock_driver = MagicMock()
        mock_driver.contexts = ["NATIVE_APP"]
        waiter = _make_waiter(driver=mock_driver)
        with pytest.raises(WaitTimeoutError):
            waiter.for_context_contains("WEBVIEW")

    def test_handles_driver_exception_gracefully(self) -> None:
        from selenium.common.exceptions import WebDriverException
        mock_driver = MagicMock()
        type(mock_driver).contexts = property(
            fget=lambda self: (_ for _ in ()).throw(WebDriverException())
        )
        waiter = _make_waiter(driver=mock_driver)
        with pytest.raises(WaitTimeoutError):
            waiter.for_context_contains("WEBVIEW")


class TestForAndroidActivity:
    def test_returns_activity_when_matches(self) -> None:
        mock_driver = MagicMock()
        mock_driver.current_activity = "com.example.MainActivity"
        waiter = _make_waiter(driver=mock_driver)
        result = waiter.for_android_activity("MainActivity")
        assert result == "com.example.MainActivity"

    def test_raises_when_activity_does_not_match(self) -> None:
        mock_driver = MagicMock()
        mock_driver.current_activity = "com.example.SplashActivity"
        waiter = _make_waiter(driver=mock_driver)
        with pytest.raises(WaitTimeoutError):
            waiter.for_android_activity("MainActivity")

    def test_handles_none_activity(self) -> None:
        mock_driver = MagicMock()
        mock_driver.current_activity = None
        waiter = _make_waiter(driver=mock_driver)
        with pytest.raises(WaitTimeoutError):
            waiter.for_android_activity("Main")


