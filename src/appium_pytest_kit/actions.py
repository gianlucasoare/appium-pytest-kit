"""Reusable high-level UI actions composed with wait utilities."""

from __future__ import annotations

from selenium.common.exceptions import WebDriverException

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
            message = f"Tap failed for locator: {locator}"
            raise ActionError(message) from exc

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
            message = f"Type failed for locator: {locator}"
            raise ActionError(message) from exc

    def text(self, locator: Locator, *, timeout: float = 10.0) -> str:
        """Read text from a visible element."""

        try:
            element = self._waiter.for_visibility(locator, timeout=timeout)
            return str(element.text)
        except WebDriverException as exc:
            message = f"Text read failed for locator: {locator}"
            raise ActionError(message) from exc

    def exists(self, locator: Locator, *, timeout: float = 2.0) -> bool:
        """Return whether an element becomes present within timeout."""

        try:
            self._waiter.for_presence(locator, timeout=timeout)
        except Exception:
            return False
        return True
