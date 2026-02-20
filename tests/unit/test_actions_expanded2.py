"""Tests for actions added in the second pass (tap gestures, text, keyboard, context)."""

from unittest.mock import MagicMock, patch

import pytest

from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.errors import ActionError, WaitTimeoutError
from appium_pytest_kit.waits import Waiter


def _make_actions(visible_el=None) -> tuple[MobileActions, MagicMock]:
    driver = MagicMock()
    driver.get_window_size.return_value = {"width": 400, "height": 800}
    driver.contexts = ["NATIVE_APP", "WEBVIEW_com.example"]
    waiter = MagicMock(spec=Waiter)
    if visible_el is not None:
        waiter.for_visibility.return_value = visible_el
    return MobileActions(driver=driver, waiter=waiter), driver


def _element_at(x: int, y: int, w: int = 100, h: int = 50) -> MagicMock:
    el = MagicMock()
    el.location = {"x": x, "y": y}
    el.size = {"width": w, "height": h}
    return el


# ---------------------------------------------------------------------------
# Tap gesture variants
# ---------------------------------------------------------------------------

class TestTapByCoordinates:
    def test_calls_perform(self) -> None:
        actions, _ = _make_actions()
        with patch("appium_pytest_kit.actions.ActionChains") as mock_cls:
            mock_chain = MagicMock()
            mock_cls.return_value = mock_chain
            actions.tap_by_coordinates(100, 200)
            mock_chain.perform.assert_called_once()

    def test_raises_action_error_on_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        actions, _ = _make_actions()
        with patch("appium_pytest_kit.actions.ActionChains", side_effect=WebDriverException):
            with pytest.raises(ActionError) as exc_info:
                actions.tap_by_coordinates(0, 0)
            assert exc_info.value.action == "tap_by_coordinates"


class TestTapCenter:
    def test_calls_tap_by_coordinates_at_element_center(self) -> None:
        el = _element_at(100, 200, w=100, h=50)
        actions, _ = _make_actions(visible_el=el)
        with patch.object(actions, "tap_by_coordinates") as mock_tap:
            actions.tap_center(("id", "btn"))
            # center should be (100 + 50, 200 + 25) = (150, 225)
            mock_tap.assert_called_once_with(150, 225)

    def test_raises_action_error_on_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        el = _element_at(0, 0)
        el.location = property(lambda self: (_ for _ in ()).throw(WebDriverException()))
        actions, _ = _make_actions()
        actions._waiter.for_visibility.side_effect = WebDriverException()
        with pytest.raises((ActionError, WebDriverException)):
            actions.tap_center(("id", "btn"))


class TestDoubleTap:
    def test_calls_perform(self) -> None:
        el = _element_at(100, 200)
        actions, _ = _make_actions(visible_el=el)
        with patch("appium_pytest_kit.actions.ActionChains") as mock_cls:
            mock_chain = MagicMock()
            mock_cls.return_value = mock_chain
            actions.double_tap(("id", "btn"))
            mock_chain.perform.assert_called_once()

    def test_raises_action_error_on_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        el = _element_at(0, 0)
        actions, _ = _make_actions(visible_el=el)
        with patch("appium_pytest_kit.actions.ActionChains", side_effect=WebDriverException):
            with pytest.raises(ActionError) as exc_info:
                actions.double_tap(("id", "btn"))
            assert exc_info.value.action == "double_tap"


class TestLongPress:
    def test_calls_perform(self) -> None:
        el = _element_at(100, 200)
        actions, _ = _make_actions(visible_el=el)
        with patch("appium_pytest_kit.actions.ActionChains") as mock_cls:
            mock_chain = MagicMock()
            mock_cls.return_value = mock_chain
            actions.long_press(("id", "item"), duration_seconds=1.5)
            mock_chain.perform.assert_called_once()

    def test_raises_action_error_on_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        el = _element_at(0, 0)
        actions, _ = _make_actions(visible_el=el)
        with patch("appium_pytest_kit.actions.ActionChains", side_effect=WebDriverException):
            with pytest.raises(ActionError) as exc_info:
                actions.long_press(("id", "item"))
            assert exc_info.value.action == "long_press"


class TestTapIfPresentFirstAvailable:
    def test_taps_first_visible(self) -> None:
        actions, _ = _make_actions()
        locators = [("id", "a"), ("id", "b")]
        tap_results = [False, True]
        with patch.object(actions, "tap_if_present", side_effect=tap_results):
            result = actions.tap_if_present_first_available(locators)
        assert result is True

    def test_returns_false_when_none_present(self) -> None:
        actions, _ = _make_actions()
        locators = [("id", "x"), ("id", "y")]
        with patch.object(actions, "tap_if_present", return_value=False):
            result = actions.tap_if_present_first_available(locators)
        assert result is False


# ---------------------------------------------------------------------------
# Text input variants
# ---------------------------------------------------------------------------

class TestTypeIfPresent:
    def test_returns_true_when_typed(self) -> None:
        mock_el = MagicMock()
        actions, _ = _make_actions(visible_el=mock_el)
        result = actions.type_if_present(("id", "field"), "hello")
        assert result is True
        mock_el.send_keys.assert_called_once_with("hello")

    def test_returns_false_when_not_visible(self) -> None:
        actions, _ = _make_actions()
        actions._waiter.for_visibility.side_effect = WaitTimeoutError("gone")
        result = actions.type_if_present(("id", "field"), "hello")
        assert result is False

    def test_clears_first_by_default(self) -> None:
        mock_el = MagicMock()
        actions, _ = _make_actions(visible_el=mock_el)
        actions.type_if_present(("id", "field"), "text", clear_first=True)
        mock_el.clear.assert_called_once()

    def test_skip_clear_when_false(self) -> None:
        mock_el = MagicMock()
        actions, _ = _make_actions(visible_el=mock_el)
        actions.type_if_present(("id", "field"), "text", clear_first=False)
        mock_el.clear.assert_not_called()


class TestTypeFirstAvailable:
    def test_types_into_first_visible(self) -> None:
        actions, _ = _make_actions()
        locators = [("id", "a"), ("id", "b")]
        mock_el = MagicMock()

        def _visibility(locator, *, timeout=None):
            if locator == ("id", "b"):
                return mock_el
            raise WaitTimeoutError("not visible")

        actions._waiter.for_visibility.side_effect = _visibility
        result = actions.type_first_available(locators, "hello")
        assert result is True
        mock_el.send_keys.assert_called_once_with("hello")

    def test_returns_false_when_none_visible(self) -> None:
        actions, _ = _make_actions()
        actions._waiter.for_visibility.side_effect = WaitTimeoutError("gone")
        result = actions.type_first_available([("id", "x"), ("id", "y")], "txt")
        assert result is False


class TestTypeIfPresentFirstAvailable:
    def test_returns_true_when_any_typed(self) -> None:
        actions, _ = _make_actions()
        with patch.object(actions, "type_if_present", side_effect=[False, True]):
            result = actions.type_if_present_first_available(
                [("id", "a"), ("id", "b")], "val"
            )
        assert result is True

    def test_returns_false_when_none_visible(self) -> None:
        actions, _ = _make_actions()
        with patch.object(actions, "type_if_present", return_value=False):
            result = actions.type_if_present_first_available(
                [("id", "x"), ("id", "y")], "val"
            )
        assert result is False


class TestTypeTextSlowly:
    def test_sends_each_char_separately(self) -> None:
        mock_el = MagicMock()
        actions, _ = _make_actions(visible_el=mock_el)
        with patch("appium_pytest_kit.actions.time") as mock_time:
            actions.type_text_slowly(("id", "f"), "abc", delay_per_char=0.05)
        assert mock_el.send_keys.call_count == 3
        mock_el.send_keys.assert_any_call("a")
        mock_el.send_keys.assert_any_call("b")
        mock_el.send_keys.assert_any_call("c")
        assert mock_time.sleep.call_count == 3

    def test_raises_action_error_on_driver_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        mock_el = MagicMock()
        mock_el.send_keys.side_effect = WebDriverException("fail")
        actions, _ = _make_actions(visible_el=mock_el)
        with patch("appium_pytest_kit.actions.time"):
            with pytest.raises(ActionError) as exc_info:
                actions.type_text_slowly(("id", "f"), "x")
            assert exc_info.value.action == "type_text_slowly"


# ---------------------------------------------------------------------------
# Read / inspect
# ---------------------------------------------------------------------------

class TestAttribute:
    def test_returns_attribute_value(self) -> None:
        mock_el = MagicMock()
        mock_el.get_attribute.return_value = "hint text"
        actions, _ = _make_actions(visible_el=mock_el)
        result = actions.attribute(("id", "field"), "hint")
        assert result == "hint text"
        mock_el.get_attribute.assert_called_once_with("hint")

    def test_raises_action_error_on_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        mock_el = MagicMock()
        mock_el.get_attribute.side_effect = WebDriverException("bad")
        actions, _ = _make_actions(visible_el=mock_el)
        with pytest.raises(ActionError) as exc_info:
            actions.attribute(("id", "field"), "hint")
        assert exc_info.value.action == "attribute"


# ---------------------------------------------------------------------------
# Scroll to element
# ---------------------------------------------------------------------------

class TestScrollToElement:
    def test_returns_when_element_visible(self) -> None:
        actions, _ = _make_actions()
        actions._waiter.for_visibility.return_value = MagicMock()
        with patch.object(actions, "scroll_down") as mock_scroll:
            actions.scroll_to_element(("id", "target"))
            mock_scroll.assert_not_called()

    def test_scrolls_down_until_found(self) -> None:
        actions, _ = _make_actions()
        call_count = 0

        def _visibility(locator, *, timeout=None):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise WaitTimeoutError("not visible")
            return MagicMock()

        actions._waiter.for_visibility.side_effect = _visibility
        with patch.object(actions, "scroll_down") as mock_scroll:
            actions.scroll_to_element(("id", "target"), max_swipes=5)
            assert mock_scroll.call_count == 2

    def test_raises_action_error_when_max_swipes_reached(self) -> None:
        actions, _ = _make_actions()
        actions._waiter.for_visibility.side_effect = WaitTimeoutError("gone")
        with patch.object(actions, "scroll_down"):
            with pytest.raises(ActionError) as exc_info:
                actions.scroll_to_element(("id", "target"), max_swipes=3)
            assert exc_info.value.action == "scroll_to_element"


# ---------------------------------------------------------------------------
# Keyboard
# ---------------------------------------------------------------------------

class TestHideKeyboard:
    def test_calls_driver_hide_keyboard(self) -> None:
        actions, driver = _make_actions()
        actions.hide_keyboard()
        driver.hide_keyboard.assert_called_once()

    def test_is_silent_on_webdriver_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        actions, driver = _make_actions()
        driver.hide_keyboard.side_effect = WebDriverException("not shown")
        actions.hide_keyboard()  # should not raise


class TestPressKeycode:
    def test_calls_driver_press_keycode(self) -> None:
        actions, driver = _make_actions()
        actions.press_keycode(66)
        driver.press_keycode.assert_called_once_with(66)

    def test_raises_action_error_on_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        actions, driver = _make_actions()
        driver.press_keycode.side_effect = WebDriverException("fail")
        with pytest.raises(ActionError) as exc_info:
            actions.press_keycode(4)
        assert exc_info.value.action == "press_keycode"


# ---------------------------------------------------------------------------
# Context / WebView
# ---------------------------------------------------------------------------

class TestIsWebviewAvailable:
    def test_returns_true_when_webview_in_contexts(self) -> None:
        actions, driver = _make_actions()
        driver.contexts = ["NATIVE_APP", "WEBVIEW_com.example"]
        assert actions.is_webview_available() is True

    def test_returns_false_when_no_webview(self) -> None:
        actions, driver = _make_actions()
        driver.contexts = ["NATIVE_APP"]
        assert actions.is_webview_available() is False

    def test_returns_false_on_driver_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        actions, driver = _make_actions()
        type(driver).contexts = property(
            fget=lambda self: (_ for _ in ()).throw(WebDriverException())
        )
        assert actions.is_webview_available() is False


class TestSwitchToWebview:
    def test_switches_to_first_webview_context(self) -> None:
        actions, driver = _make_actions()
        driver.contexts = ["NATIVE_APP", "WEBVIEW_com.example"]
        actions.switch_to_webview()
        driver.switch_to.context.assert_called_once_with("WEBVIEW_com.example")

    def test_raises_action_error_when_no_webview(self) -> None:
        actions, driver = _make_actions()
        driver.contexts = ["NATIVE_APP"]
        with pytest.raises(ActionError) as exc_info:
            actions.switch_to_webview()
        assert exc_info.value.action == "switch_to_webview"


class TestSwitchToNative:
    def test_switches_to_native_app(self) -> None:
        actions, driver = _make_actions()
        actions.switch_to_native()
        driver.switch_to.context.assert_called_once_with("NATIVE_APP")

    def test_raises_action_error_on_exception(self) -> None:
        from selenium.common.exceptions import WebDriverException
        actions, driver = _make_actions()
        driver.switch_to.context.side_effect = WebDriverException("fail")
        with pytest.raises(ActionError) as exc_info:
            actions.switch_to_native()
        assert exc_info.value.action == "switch_to_native"
