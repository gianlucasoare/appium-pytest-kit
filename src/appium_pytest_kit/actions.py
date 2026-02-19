"""Reusable high-level UI actions composed with wait utilities."""


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

    def tap(self, locator: Locator, *, timeout: float = 10.0) -> None:
        """Tap a visible element."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            element.click()
        except WebDriverException as exc:
            raise ActionError(
                f"Tap failed for locator: {locator}", locator=locator, action="tap"
            ) from exc

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

    def tap_if_present(self, locator: Locator, *, timeout: float = 2.0) -> bool:
        """Tap element if visible within timeout. Returns True if tapped."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            element.click()
            return True
        except Exception:
            return False

    def clear(self, locator: Locator, *, timeout: float = 10.0) -> None:
        """Clear the text content of an element."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            element.clear()
        except WebDriverException as exc:
            raise ActionError(
                f"Clear failed for locator: {locator}", locator=locator, action="clear"
            ) from exc

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
