"""Reusable high-level UI actions composed with wait utilities."""


import time
from collections.abc import Iterable

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from appium_pytest_kit.errors import ActionError
from appium_pytest_kit.waits import Locator, Waiter


class MobileActions:
    """Driver action helpers that stay generic and app-independent."""

    def __init__(self, driver, waiter: Waiter) -> None:
        self._driver = driver
        self._waiter = waiter

    # ------------------------------------------------------------------
    # Tap / click
    # ------------------------------------------------------------------

    def tap(self, locator: Locator, *, timeout: float = 10.0) -> None:
        """Tap a visible element."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            element.click()
        except WebDriverException as exc:
            raise ActionError(
                f"Tap failed for locator: {locator}", locator=locator, action="tap"
            ) from exc

    def tap_if_present(self, locator: Locator, *, timeout: float = 2.0) -> bool:
        """Tap element if visible within timeout. Returns True if tapped."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            element.click()
            return True
        except Exception:
            return False

    def tap_if_present_first_available(
        self,
        locators: Iterable[Locator],
        *,
        timeout: float = 2.0,
    ) -> bool:
        """Tap the first locator that is visible within timeout. Returns True if any tapped."""

        for locator in locators:
            if self.tap_if_present(locator, timeout=timeout):
                return True
        return False

    def type_first_available(
        self,
        locators: Iterable[Locator],
        value: str,
        *,
        clear_first: bool = True,
        timeout: float = 10.0,
    ) -> bool:
        """Type text into the first visible locator. Returns True if any succeeded."""

        for locator in locators:
            try:
                element = self._waiter.for_visibility(locator, timeout=timeout)
                if clear_first:
                    element.clear()
                element.send_keys(value)
                return True
            except Exception:
                pass
        return False

    def type_if_present_first_available(
        self,
        locators: Iterable[Locator],
        value: str,
        *,
        clear_first: bool = True,
        timeout: float = 3.0,
    ) -> bool:
        """Type into the first visible locator within a short timeout. Returns True if typed."""

        for locator in locators:
            if self.type_if_present(locator, value, clear_first=clear_first, timeout=timeout):
                return True
        return False

    def tap_by_coordinates(self, x: int, y: int) -> None:
        """Tap at absolute screen coordinates (x, y)."""

        try:
            actions = ActionChains(self._driver)
            actions.w3c_actions = ActionBuilder(
                self._driver,
                mouse=PointerInput(interaction.POINTER_TOUCH, "touch"),
            )
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.05)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
        except WebDriverException as exc:
            raise ActionError(
                f"Tap at coordinates ({x},{y}) failed", action="tap_by_coordinates"
            ) from exc

    def tap_center(self, locator: Locator, *, timeout: float = 10.0) -> None:
        """Tap the visual center of an element."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            loc = element.location
            size = element.size
            center_x = int(loc["x"] + size["width"] / 2)
            center_y = int(loc["y"] + size["height"] / 2)
            self.tap_by_coordinates(center_x, center_y)
        except WebDriverException as exc:
            raise ActionError(
                f"Tap center failed for locator: {locator}", locator=locator, action="tap_center"
            ) from exc

    def double_tap(self, locator: Locator, *, timeout: float = 10.0) -> None:
        """Double-tap a visible element."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            loc = element.location
            size = element.size
            x = int(loc["x"] + size["width"] / 2)
            y = int(loc["y"] + size["height"] / 2)
            actions = ActionChains(self._driver)
            actions.w3c_actions = ActionBuilder(
                self._driver,
                mouse=PointerInput(interaction.POINTER_TOUCH, "touch"),
            )
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.05)
            actions.w3c_actions.pointer_action.release()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.05)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
        except WebDriverException as exc:
            raise ActionError(
                f"Double tap failed for locator: {locator}", locator=locator, action="double_tap"
            ) from exc

    def long_press(
        self,
        locator: Locator,
        *,
        duration_seconds: float = 2.0,
        timeout: float = 10.0,
    ) -> None:
        """Long-press a visible element for the given duration."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            loc = element.location
            size = element.size
            x = int(loc["x"] + size["width"] / 2)
            y = int(loc["y"] + size["height"] / 2)
            actions = ActionChains(self._driver)
            actions.w3c_actions = ActionBuilder(
                self._driver,
                mouse=PointerInput(interaction.POINTER_TOUCH, "touch"),
            )
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(duration_seconds)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
        except WebDriverException as exc:
            raise ActionError(
                f"Long press failed for locator: {locator}", locator=locator, action="long_press"
            ) from exc

    # ------------------------------------------------------------------
    # Text input
    # ------------------------------------------------------------------

    def type_text(
        self,
        locator: Locator,
        value: str,
        *,
        clear_first: bool = True,
        timeout: float = 10.0,
    ) -> None:
        """Type text into a visible element."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            if clear_first:
                element.clear()
            element.send_keys(value)
        except WebDriverException as exc:
            raise ActionError(
                f"Type failed for locator: {locator}", locator=locator, action="type_text"
            ) from exc

    def type_if_present(
        self,
        locator: Locator,
        value: str,
        *,
        clear_first: bool = True,
        timeout: float = 3.0,
    ) -> bool:
        """Type text into element if visible within timeout. Returns True if typed."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            if clear_first:
                element.clear()
            element.send_keys(value)
            return True
        except Exception:
            return False

    def type_text_slowly(
        self,
        locator: Locator,
        value: str,
        *,
        delay_per_char: float = 0.1,
        clear_first: bool = True,
        timeout: float = 10.0,
    ) -> None:
        """Type text character-by-character with a delay between each keystroke.

        Useful for apps that drop characters under fast input.
        """

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            if clear_first:
                element.clear()
            for char in value:
                element.send_keys(char)
                time.sleep(delay_per_char)
        except WebDriverException as exc:
            raise ActionError(
                f"Slow type failed for locator: {locator}",
                locator=locator,
                action="type_text_slowly"
            ) from exc

    def clear(self, locator: Locator, *, timeout: float = 10.0) -> None:
        """Clear the text content of an element."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            element.clear()
        except WebDriverException as exc:
            raise ActionError(
                f"Clear failed for locator: {locator}", locator=locator, action="clear"
            ) from exc

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def is_displayed(self, locator: Locator, *, timeout: float | None = None) -> bool:
        """Return True if the element is visible within timeout, False otherwise.

        Unlike `exists()` which checks DOM presence, this checks full visibility.
        Defaults to the waiter's default_timeout when no timeout is given.
        """

        effective_timeout = timeout if timeout is not None else self._waiter.default_timeout
        try:
            self._waiter.for_visibility(locator, timeout=effective_timeout)
            return True
        except Exception:
            return False

    def assert_displayed(self, locator: Locator, *, timeout: float | None = None) -> None:
        """Assert that the element is visible. Raises AssertionError if not."""

        effective_timeout = timeout if timeout is not None else self._waiter.default_timeout
        if not self.is_displayed(locator, timeout=effective_timeout):
            msg = f"Element not displayed within {effective_timeout}s: {locator}"
            raise AssertionError(msg)

    def is_displayed_first_available(
        self,
        locators: Iterable[Locator],
        *,
        timeout: float = 1.0,
    ) -> bool:
        """Return True if any locator in the list is visible within timeout."""

        return any(self.is_displayed(locator, timeout=timeout) for locator in locators)

    def assert_displayed_first_available(
        self,
        locators: Iterable[Locator],
        *,
        timeout: float | None = None,
    ) -> None:
        """Assert that at least one locator in the list is visible.

        Raises AssertionError if none are visible within timeout.
        """

        locs = list(locators)
        effective_timeout = timeout if timeout is not None else self._waiter.default_timeout
        if not self.is_displayed_first_available(locs, timeout=effective_timeout):
            msg = f"None of the locators were displayed within {effective_timeout}s: {locs}"
            raise AssertionError(msg)

    def not_displayed_first_available(
        self,
        locators: Iterable[Locator],
        *,
        timeout: float = 1.0,
    ) -> bool:
        """Return True if all locators in the list are NOT visible within timeout."""

        return not any(self.is_displayed(locator, timeout=timeout) for locator in locators)

    def assert_not_displayed_first_available(
        self,
        locators: Iterable[Locator],
        *,
        timeout: float | None = None,
    ) -> None:
        """Assert that none of the locators are visible. Raises AssertionError if any is shown."""

        locs = list(locators)
        effective_timeout = timeout if timeout is not None else self._waiter.default_timeout
        if not self.not_displayed_first_available(locs, timeout=effective_timeout):
            msg = (
                f"At least one locator was unexpectedly displayed"
                f" within {effective_timeout}s: {locs}"
            )
            raise AssertionError(msg)

    # ------------------------------------------------------------------
    # Read / inspect
    # ------------------------------------------------------------------

    def text(self, locator: Locator, *, timeout: float = 10.0) -> str:
        """Read text from a visible element."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            return str(element.text)
        except WebDriverException as exc:
            raise ActionError(
                f"Text read failed for locator: {locator}", locator=locator, action="text"
            ) from exc

    def exists(self, locator: Locator, *, timeout: float = 2.0) -> bool:
        """Return whether an element becomes present within timeout."""

        try:
            self._waiter.for_presence(locator, timeout=timeout)
        except Exception:
            return False
        return True

    def attribute(
        self,
        locator: Locator,
        attr: str,
        *,
        timeout: float = 10.0,
    ) -> str | None:
        """Return the value of *attr* on a visible element, or None."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            return element.get_attribute(attr)
        except WebDriverException as exc:
            raise ActionError(
                f"Attribute read failed for locator: {locator}", locator=locator, action="attribute"
            ) from exc

    # ------------------------------------------------------------------
    # Swipe / scroll
    # ------------------------------------------------------------------

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        *,
        duration_ms: int = 800,
    ) -> None:
        """Perform a swipe gesture using W3C Pointer Actions."""

        try:
            actions = ActionChains(self._driver)
            actions.w3c_actions = ActionBuilder(
                self._driver,
                mouse=PointerInput(interaction.POINTER_TOUCH, "touch"),
            )
            actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(duration_ms / 1000)
            actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
        except WebDriverException as exc:
            raise ActionError(
                f"Swipe failed ({start_x},{start_y})->({end_x},{end_y})", action="swipe"
            ) from exc

    def scroll_down(self, *, swipe_fraction: float = 0.5) -> None:
        """Scroll down by swiping upward across the screen center."""

        size = self._driver.get_window_size()
        width = size["width"]
        height = size["height"]
        start_x = width // 2
        start_y = int(height * (0.5 + swipe_fraction / 2))
        end_y = int(height * (0.5 - swipe_fraction / 2))
        self.swipe(start_x, start_y, start_x, end_y)

    def scroll_up(self, *, swipe_fraction: float = 0.5) -> None:
        """Scroll up by swiping downward across the screen center."""

        size = self._driver.get_window_size()
        width = size["width"]
        height = size["height"]
        start_x = width // 2
        start_y = int(height * (0.5 - swipe_fraction / 2))
        end_y = int(height * (0.5 + swipe_fraction / 2))
        self.swipe(start_x, start_y, start_x, end_y)

    def scroll_to_element(
        self,
        locator: Locator,
        *,
        direction: str = "down",
        max_swipes: int = 10,
        swipe_fraction: float = 0.4,
    ) -> None:
        """Scroll until the element is visible or max_swipes is reached."""

        for _ in range(max_swipes):
            try:
                self._waiter.for_visibility(locator, timeout=1.5)
                return
            except Exception:
                pass
            if direction == "down":
                self.scroll_down(swipe_fraction=swipe_fraction)
            else:
                self.scroll_up(swipe_fraction=swipe_fraction)

        raise ActionError(
            f"Element not found after {max_swipes} swipes: {locator}",
            locator=locator,
            action="scroll_to_element",
        )

    # ------------------------------------------------------------------
    # Keyboard
    # ------------------------------------------------------------------

    def hide_keyboard(self) -> None:
        """Dismiss the on-screen keyboard if it is visible."""

        try:
            self._driver.hide_keyboard()
        except WebDriverException:
            pass  # keyboard may already be hidden — non-fatal

    def press_keycode(self, keycode: int) -> None:
        """Press an Android keycode (no-op on iOS).

        Common keycodes:
        - 4  = BACK
        - 3  = HOME
        - 66 = ENTER
        - 67 = BACKSPACE
        """

        try:
            self._driver.press_keycode(keycode)
        except WebDriverException as exc:
            raise ActionError(
                f"press_keycode({keycode}) failed", action="press_keycode"
            ) from exc

    # ------------------------------------------------------------------
    # Context switching (hybrid apps)
    # ------------------------------------------------------------------

    def is_webview_available(self) -> bool:
        """Return True if a WEBVIEW context is available."""

        try:
            return any("WEBVIEW" in ctx for ctx in self._driver.contexts)
        except WebDriverException:
            return False

    def switch_to_webview(self) -> None:
        """Switch the driver to the first available WEBVIEW context."""

        try:
            contexts = self._driver.contexts
            for ctx in contexts:
                if "WEBVIEW" in ctx:
                    self._driver.switch_to.context(ctx)
                    return
            msg = "No WEBVIEW context found"
            raise ActionError(msg, action="switch_to_webview")
        except WebDriverException as exc:
            raise ActionError("switch_to_webview failed", action="switch_to_webview") from exc

    def switch_to_native(self) -> None:
        """Switch the driver back to the NATIVE_APP context."""

        try:
            self._driver.switch_to.context("NATIVE_APP")
        except WebDriverException as exc:
            raise ActionError("switch_to_native failed", action="switch_to_native") from exc
