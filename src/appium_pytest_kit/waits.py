"""Generic explicit wait primitives for mobile UI interactions."""


import logging
from collections.abc import Callable, Iterable
from typing import TypeVar

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from appium_pytest_kit.errors import WaitTimeoutError

logger = logging.getLogger(__name__)

ConditionResult = TypeVar("ConditionResult")
Locator = tuple[str, str]
Locators = Iterable[Locator]


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

    @property
    def default_timeout(self) -> float:
        """The default wait timeout in seconds."""
        return self._default_timeout

    def until(
        self,
        condition: Callable[[object], ConditionResult],
        *,
        timeout: float | None = None,
        message: str = "",
        locator: Locator | None = None,
    ) -> ConditionResult:
        """Wait until a custom condition is truthy and return its value."""

        effective_timeout = timeout or self._default_timeout
        wait = WebDriverWait(
            self._driver,
            effective_timeout,
            poll_frequency=self._poll_frequency,
        )
        try:
            return wait.until(condition, message)
        except TimeoutException as exc:
            raise WaitTimeoutError(
                message or "Explicit wait timed out",
                locator=locator,
                timeout=effective_timeout,
            ) from exc

    def for_presence(self, locator: Locator, *, timeout: float | None = None):
        """Wait for element presence and return it."""

        t = timeout or self._default_timeout
        logger.debug("wait:presence  %s  timeout=%.1fs", locator, t)
        return self.until(
            ec.presence_of_element_located(locator),
            timeout=timeout,
            message=f"Element not present: {locator}",
            locator=locator,
        )

    def for_visibility(self, locator: Locator, *, timeout: float | None = None):
        """Wait for element visibility and return it."""

        t = timeout or self._default_timeout
        logger.debug("wait:visibility  %s  timeout=%.1fs", locator, t)
        return self.until(
            ec.visibility_of_element_located(locator),
            timeout=timeout,
            message=f"Element not visible: {locator}",
            locator=locator,
        )

    def for_clickable(self, locator: Locator, *, timeout: float | None = None):
        """Wait for element to be clickable and return it."""

        t = timeout or self._default_timeout
        logger.debug("wait:clickable  %s  timeout=%.1fs", locator, t)
        return self.until(
            ec.element_to_be_clickable(locator),
            timeout=timeout,
            message=f"Element not clickable: {locator}",
            locator=locator,
        )

    def for_invisibility(self, locator: Locator, *, timeout: float | None = None) -> bool:
        """Wait for element to be invisible (or absent) and return True."""

        t = timeout or self._default_timeout
        logger.debug("wait:invisibility  %s  timeout=%.1fs", locator, t)
        return self.until(
            ec.invisibility_of_element_located(locator),
            timeout=timeout,
            message=f"Element still visible: {locator}",
            locator=locator,
        )

    def for_text_contains(
        self,
        locator: Locator,
        text: str,
        *,
        timeout: float | None = None,
    ):
        """Wait until element text contains substring, return True."""

        t = timeout or self._default_timeout
        logger.debug("wait:text_contains  %s  text=%r  timeout=%.1fs", locator, text, t)
        return self.until(
            ec.text_to_be_present_in_element(locator, text),
            timeout=timeout,
            message=f"Text {text!r} not found in element: {locator}",
            locator=locator,
        )

    def for_text_equals(
        self,
        locator: Locator,
        text: str,
        *,
        timeout: float | None = None,
    ):
        """Wait until element text exactly matches, return element."""

        t = timeout or self._default_timeout
        logger.debug("wait:text_equals  %s  text=%r  timeout=%.1fs", locator, text, t)

        def _exact_match(driver):
            try:
                el = driver.find_element(*locator)
                return el if el.text == text else False
            except Exception:
                return False

        return self.until(
            _exact_match,
            timeout=timeout,
            message=f"Text {text!r} not matched in element: {locator}",
            locator=locator,
        )

    def for_all_visible(
        self,
        locators: Locators,
        *,
        timeout: float | None = None,
    ) -> list:
        """Wait until all elements are visible simultaneously and return them.

        Uses a single wait that polls until every locator is visible at the same
        instant, so the timeout applies to the whole group rather than each element
        individually.
        """

        locs = list(locators)
        if not locs:
            return []

        t = timeout or self._default_timeout
        logger.debug("wait:all_visible  %d locators  timeout=%.1fs", len(locs), t)

        def _all_visible(driver):
            try:
                elements = [ec.visibility_of_element_located(loc)(driver) for loc in locs]
                return elements if all(elements) else False
            except Exception:
                return False

        return self.until(
            _all_visible,
            timeout=timeout,
            message=f"Not all elements became visible: {locs}",
        )

    def for_all_gone(
        self,
        locators: Locators,
        *,
        timeout: float | None = None,
    ) -> bool:
        """Wait until every locator in the list is invisible or absent."""

        locators_list = list(locators)
        t = timeout or self._default_timeout
        logger.debug("wait:all_gone  %d locators  timeout=%.1fs", len(locators_list), t)

        def _all_gone(driver):
            for locator in locators_list:
                try:
                    result = ec.invisibility_of_element_located(locator)(driver)
                    if not result:
                        return False
                except Exception:
                    pass
            return True

        return self.until(
            _all_gone,
            timeout=timeout,
            message=f"Some elements still visible: {locators_list!r}",
        )

    def for_context_contains(
        self,
        substring: str,
        *,
        timeout: float | None = None,
    ) -> str:
        """Wait until a driver context name contains *substring* and return it.

        Useful for hybrid apps waiting for a WEBVIEW context to become available.
        """

        t = timeout or self._default_timeout
        logger.debug("wait:context_contains  %r  timeout=%.1fs", substring, t)

        def _cond(driver):
            try:
                for ctx in driver.contexts:
                    if substring in ctx:
                        return ctx
            except Exception:
                pass
            return False

        return self.until(
            _cond,
            timeout=timeout,
            message=f"No context containing {substring!r} became available",
        )

    def for_android_activity(
        self,
        partial_name: str,
        *,
        timeout: float | None = None,
    ) -> str:
        """Wait until the current Android activity name contains *partial_name*.

        Returns the full activity name. No-op / always-true on iOS.
        """

        t = timeout or self._default_timeout
        logger.debug("wait:android_activity  %r  timeout=%.1fs", partial_name, t)

        def _cond(driver):
            try:
                activity = driver.current_activity or ""
                return activity if partial_name in activity else False
            except Exception:
                return False

        return self.until(
            _cond,
            timeout=timeout,
            message=f"Activity containing {partial_name!r} did not appear",
        )

    def for_any_visible(self, locators: Locators, *, timeout: float | None = None):
        """Wait until any one of the locators is visible and return it."""

        locators_list = list(locators)
        t = timeout or self._default_timeout
        logger.debug("wait:any_visible  %d locators  timeout=%.1fs", len(locators_list), t)

        def _any_visible(driver):
            for locator in locators_list:
                try:
                    el = ec.visibility_of_element_located(locator)(driver)
                    if el:
                        return el
                except Exception:
                    pass
            return False

        return self.until(
            _any_visible,
            timeout=timeout,
            message=f"None of {locators_list!r} became visible",
        )
