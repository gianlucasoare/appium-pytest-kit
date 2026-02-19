"""Generic explicit wait primitives for mobile UI interactions."""


from collections.abc import Callable
from typing import TypeVar

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from appium_pytest_kit.errors import WaitTimeoutError

ConditionResult = TypeVar("ConditionResult")
Locator = tuple[str, str]


class Waiter:
    """Thin wrapper over Selenium wait APIs with framework-level errors."""

    def __init__(
        self,
        driver,
        *,
        default_timeout: float = 10.0,
        poll_frequency: float = 0.5,
    ) -> None:
        self._driver = driver
        self._default_timeout = default_timeout
        self._poll_frequency = poll_frequency

    def until(
        self,
        condition: Callable[[object], ConditionResult],
        *,
        timeout: float | None = None,
        message: str = "",
    ) -> ConditionResult:
        """Wait until a custom condition is truthy and return its value."""

        wait = WebDriverWait(
            self._driver,
            timeout or self._default_timeout,
            poll_frequency=self._poll_frequency,
        )
        try:
            return wait.until(condition, message)
        except TimeoutException as exc:
            raise WaitTimeoutError(message or "Explicit wait timed out") from exc

    def for_presence(self, locator: Locator, *, timeout: float | None = None):
        """Wait for element presence and return it."""

        return self.until(
            ec.presence_of_element_located(locator),
            timeout=timeout,
            message=f"Element not present: {locator}",
        )

    def for_visibility(self, locator: Locator, *, timeout: float | None = None):
        """Wait for element visibility and return it."""

        return self.until(
            ec.visibility_of_element_located(locator),
            timeout=timeout,
            message=f"Element not visible: {locator}",
        )
