"""Tests for the expanded Waiter methods."""

from unittest.mock import MagicMock, patch

import pytest

from appium_pytest_kit.errors import WaitTimeoutError
from appium_pytest_kit.waits import Waiter


def _make_waiter(driver=None, timeout: float = 0.1) -> Waiter:
    driver = driver or MagicMock()
    return Waiter(driver, default_timeout=timeout, poll_frequency=0.05)


class TestForClickable:
    def test_returns_element_when_clickable(self) -> None:
        waiter = _make_waiter()
        mock_el = MagicMock()
        with patch(
            "selenium.webdriver.support.expected_conditions.element_to_be_clickable",
            return_value=lambda d: mock_el,
        ):
            result = waiter.for_clickable(("id", "btn"))
        assert result is mock_el

    def test_raises_on_timeout(self) -> None:
        waiter = _make_waiter()
        with patch(
            "selenium.webdriver.support.expected_conditions.element_to_be_clickable",
            return_value=lambda d: False,
        ):
            with pytest.raises(WaitTimeoutError):
                waiter.for_clickable(("id", "btn"))


class TestForInvisibility:
    def test_returns_true_when_invisible(self) -> None:
        waiter = _make_waiter()
        with patch(
            "selenium.webdriver.support.expected_conditions.invisibility_of_element_located",
            return_value=lambda d: True,
        ):
            result = waiter.for_invisibility(("id", "modal"))
        assert result is True

    def test_raises_on_timeout(self) -> None:
        waiter = _make_waiter()
        with patch(
            "selenium.webdriver.support.expected_conditions.invisibility_of_element_located",
            return_value=lambda d: False,
        ):
            with pytest.raises(WaitTimeoutError):
                waiter.for_invisibility(("id", "modal"))


class TestForTextContains:
    def test_returns_true_when_text_present(self) -> None:
        waiter = _make_waiter()
        with patch(
            "selenium.webdriver.support.expected_conditions.text_to_be_present_in_element",
            return_value=lambda d: True,
        ):
            result = waiter.for_text_contains(("id", "label"), "hello")
        assert result is True

    def test_raises_on_timeout(self) -> None:
        waiter = _make_waiter()
        with patch(
            "selenium.webdriver.support.expected_conditions.text_to_be_present_in_element",
            return_value=lambda d: False,
        ):
            with pytest.raises(WaitTimeoutError):
                waiter.for_text_contains(("id", "label"), "hello")


class TestForTextEquals:
    def test_returns_element_on_exact_match(self) -> None:
        mock_el = MagicMock()
        mock_el.text = "exact"
        mock_driver = MagicMock()
        mock_driver.find_element.return_value = mock_el
        waiter = _make_waiter(driver=mock_driver)

        result = waiter.for_text_equals(("id", "lbl"), "exact")
        assert result is mock_el

    def test_raises_when_text_does_not_match(self) -> None:
        mock_el = MagicMock()
        mock_el.text = "different"
        mock_driver = MagicMock()
        mock_driver.find_element.return_value = mock_el
        waiter = _make_waiter(driver=mock_driver)

        with pytest.raises(WaitTimeoutError):
            waiter.for_text_equals(("id", "lbl"), "expected")


class TestForAllVisible:
    def test_returns_list_of_elements(self) -> None:
        waiter = _make_waiter()
        el_a, el_b = MagicMock(), MagicMock()
        locator_map = {("id", "a"): el_a, ("id", "b"): el_b}
        locators = list(locator_map)

        def _mock_condition(locator):
            return lambda _driver: locator_map[locator]

        with patch(
            "selenium.webdriver.support.expected_conditions.visibility_of_element_located",
            side_effect=_mock_condition,
        ):
            result = waiter.for_all_visible(locators)

        assert result == [el_a, el_b]

    def test_returns_empty_list_for_no_locators(self) -> None:
        waiter = _make_waiter()
        assert waiter.for_all_visible([]) == []

    def test_raises_when_one_is_not_visible(self) -> None:
        waiter = _make_waiter()
        locators = [("id", "a"), ("id", "b")]

        # ("id", "b") returns False — the group condition stays falsy → timeout
        def _mock_condition(locator):
            if locator == ("id", "b"):
                return lambda _driver: False
            return lambda _driver: MagicMock()

        with patch(
            "selenium.webdriver.support.expected_conditions.visibility_of_element_located",
            side_effect=_mock_condition,
        ):
            with pytest.raises(WaitTimeoutError):
                waiter.for_all_visible(locators)


class TestForAnyVisible:
    def test_returns_first_visible_element(self) -> None:
        mock_el = MagicMock()
        mock_driver = MagicMock()
        # The inner condition will be called once with the driver
        call_count = 0

        def fake_run(cmd, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_el

        waiter = _make_waiter(driver=mock_driver)
        locators = [("id", "a"), ("id", "b")]

        with patch(
            "selenium.webdriver.support.expected_conditions.visibility_of_element_located",
            return_value=lambda d: mock_el,
        ):
            result = waiter.for_any_visible(locators)

        assert result is mock_el

    def test_raises_when_none_visible(self) -> None:
        mock_driver = MagicMock()
        waiter = _make_waiter(driver=mock_driver)
        locators = [("id", "x"), ("id", "y")]

        with patch(
            "selenium.webdriver.support.expected_conditions.visibility_of_element_located",
            return_value=lambda d: False,
        ):
            with pytest.raises(WaitTimeoutError):
                waiter.for_any_visible(locators)


class TestWaitTimeoutErrorContext:
    def test_error_carries_timeout(self) -> None:
        waiter = _make_waiter(timeout=0.1)
        with patch(
            "selenium.webdriver.support.expected_conditions.visibility_of_element_located",
            return_value=lambda d: False,
        ):
            with pytest.raises(WaitTimeoutError) as exc_info:
                waiter.for_visibility(("id", "btn"), timeout=0.1)

        assert exc_info.value.timeout == 0.1
        assert exc_info.value.locator == ("id", "btn")
