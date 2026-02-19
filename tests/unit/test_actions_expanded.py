"""Tests for the expanded MobileActions methods."""

from unittest.mock import MagicMock, patch

import pytest

from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.errors import ActionError, WaitTimeoutError
from appium_pytest_kit.waits import Waiter


def _make_actions(visible_el=None, timeout: float = 0.1) -> tuple[MobileActions, MagicMock]:
    driver = MagicMock()
    driver.get_window_size.return_value = {"width": 400, "height": 800}
    waiter = MagicMock(spec=Waiter)
    if visible_el is not None:
        waiter.for_visibility.return_value = visible_el
    actions = MobileActions(driver=driver, waiter=waiter)
    return actions, driver


class TestTapIfPresent:
    def test_returns_true_when_element_tapped(self) -> None:
        mock_el = MagicMock()
        actions, _ = _make_actions(visible_el=mock_el)
        result = actions.tap_if_present(("id", "btn"))
        assert result is True
        mock_el.click.assert_called_once()

    def test_returns_false_when_not_present(self) -> None:
        actions, _ = _make_actions()
        actions._waiter.for_visibility.side_effect = WaitTimeoutError("gone")
        result = actions.tap_if_present(("id", "missing"))
        assert result is False


class TestClear:
    def test_clear_calls_element_clear(self) -> None:
        mock_el = MagicMock()
        actions, _ = _make_actions(visible_el=mock_el)
        actions.clear(("id", "field"))
        mock_el.clear.assert_called_once()

    def test_clear_raises_action_error_on_driver_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException

        mock_el = MagicMock()
        mock_el.clear.side_effect = WebDriverException("fail")
        actions, _ = _make_actions(visible_el=mock_el)
        with pytest.raises(ActionError) as exc_info:
            actions.clear(("id", "field"))
        assert exc_info.value.action == "clear"


class TestSwipe:
    def test_swipe_calls_actions_perform(self) -> None:
        actions, _driver = _make_actions()

        with patch("appium_pytest_kit.actions.ActionChains") as mock_ac_cls:
            mock_ac = MagicMock()
            mock_ac_cls.return_value = mock_ac
            mock_ac.w3c_actions = MagicMock()

            actions.swipe(100, 600, 100, 200)

            mock_ac.perform.assert_called_once()

    def test_swipe_raises_action_error_on_driver_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException

        actions, _ = _make_actions()
        with patch(
            "appium_pytest_kit.actions.ActionChains",
            side_effect=WebDriverException("driver error"),
        ):
            with pytest.raises(ActionError) as exc_info:
                actions.swipe(0, 0, 100, 100)
            assert exc_info.value.action == "swipe"


class TestScrollDown:
    def test_scroll_down_calls_swipe(self) -> None:
        actions, _ = _make_actions()
        with patch.object(actions, "swipe") as mock_swipe:
            actions.scroll_down(swipe_fraction=0.5)
            mock_swipe.assert_called_once()
            start_x, start_y, end_x, end_y = mock_swipe.call_args[0]
            assert start_x == end_x  # vertical swipe
            assert start_y > end_y  # swipe upward = scroll down


class TestScrollUp:
    def test_scroll_up_calls_swipe(self) -> None:
        actions, _ = _make_actions()
        with patch.object(actions, "swipe") as mock_swipe:
            actions.scroll_up(swipe_fraction=0.5)
            mock_swipe.assert_called_once()
            start_x, start_y, end_x, end_y = mock_swipe.call_args[0]
            assert start_x == end_x
            assert start_y < end_y  # swipe downward = scroll up


class TestActionErrorContext:
    def test_tap_error_carries_action_and_locator(self) -> None:
        from selenium.common.exceptions import WebDriverException

        mock_el = MagicMock()
        mock_el.click.side_effect = WebDriverException("boom")
        actions, _ = _make_actions(visible_el=mock_el)
        with pytest.raises(ActionError) as exc_info:
            actions.tap(("id", "btn"))
        err = exc_info.value
        assert err.action == "tap"
        assert err.locator == ("id", "btn")

    def test_type_text_error_carries_context(self) -> None:
        from selenium.common.exceptions import WebDriverException

        mock_el = MagicMock()
        mock_el.send_keys.side_effect = WebDriverException("fail")
        actions, _ = _make_actions(visible_el=mock_el)
        with pytest.raises(ActionError) as exc_info:
            actions.type_text(("id", "field"), "hello")
        assert exc_info.value.action == "type_text"
