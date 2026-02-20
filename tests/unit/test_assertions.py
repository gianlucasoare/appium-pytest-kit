"""Unit tests for MobileActions assertion methods."""

from unittest.mock import MagicMock

import pytest

from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.waits import Waiter


def _make_actions(driver=None, timeout: float = 0.1) -> MobileActions:
    driver = driver or MagicMock()
    waiter = Waiter(driver, default_timeout=timeout, poll_frequency=0.05)
    return MobileActions(driver, waiter)


def _visible_waiter(driver: MagicMock) -> None:
    """Configure driver so find_element returns a displayed element."""
    el = MagicMock()
    el.is_displayed.return_value = True
    driver.find_element.return_value = el
    driver.find_elements.return_value = [el]


def _invisible_waiter(driver: MagicMock) -> None:
    """Configure driver so find_element returns an element that is NOT displayed."""
    el = MagicMock()
    el.is_displayed.return_value = False
    driver.find_element.return_value = el
    driver.find_elements.return_value = []


LOC_A = ("id", "elementA")
LOC_B = ("id", "elementB")


class TestIsDisplayed:
    def test_returns_true_when_visible(self) -> None:
        driver = MagicMock()
        _visible_waiter(driver)
        actions = _make_actions(driver)
        assert actions.is_displayed(LOC_A) is True

    def test_returns_false_when_not_visible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        assert actions.is_displayed(LOC_A) is False

    def test_returns_false_on_exception(self) -> None:
        driver = MagicMock()
        driver.find_element.side_effect = Exception("boom")
        actions = _make_actions(driver)
        assert actions.is_displayed(LOC_A) is False


class TestAssertDisplayed:
    def test_passes_when_element_visible(self) -> None:
        driver = MagicMock()
        _visible_waiter(driver)
        actions = _make_actions(driver)
        # Should not raise
        actions.assert_displayed(LOC_A)

    def test_raises_when_element_not_visible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="not displayed"):
            actions.assert_displayed(LOC_A)

    def test_uses_default_timeout_when_none_given(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver, timeout=0.1)
        with pytest.raises(AssertionError, match=r"0\.1s"):
            actions.assert_displayed(LOC_A)

    def test_uses_explicit_timeout(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match=r"5\.0s"):
            actions.assert_displayed(LOC_A, timeout=5.0)


class TestIsDisplayedFirstAvailable:
    def test_returns_true_if_any_visible(self) -> None:
        driver = MagicMock()

        visible_el = MagicMock()
        visible_el.is_displayed.return_value = True
        hidden_el = MagicMock()
        hidden_el.is_displayed.return_value = False

        def _find(by, value):
            if value == "elementA":
                raise Exception("not found")
            return visible_el

        driver.find_element.side_effect = _find
        driver.find_elements.return_value = [visible_el]
        actions = _make_actions(driver)
        assert actions.is_displayed_first_available([LOC_A, LOC_B]) is True

    def test_returns_false_when_none_visible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        assert actions.is_displayed_first_available([LOC_A, LOC_B]) is False

    def test_empty_list_returns_false(self) -> None:
        actions = _make_actions()
        assert actions.is_displayed_first_available([]) is False


class TestAssertDisplayedFirstAvailable:
    def test_passes_when_one_visible(self) -> None:
        driver = MagicMock()
        _visible_waiter(driver)
        actions = _make_actions(driver)
        actions.assert_displayed_first_available([LOC_A, LOC_B])

    def test_raises_when_none_visible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="None of the locators"):
            actions.assert_displayed_first_available([LOC_A, LOC_B])

    def test_error_lists_locators(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        with pytest.raises(AssertionError) as exc_info:
            actions.assert_displayed_first_available([LOC_A])
        assert "elementA" in str(exc_info.value)


class TestNotDisplayedFirstAvailable:
    def test_returns_true_when_none_visible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        assert actions.not_displayed_first_available([LOC_A, LOC_B]) is True

    def test_returns_false_when_any_visible(self) -> None:
        driver = MagicMock()
        _visible_waiter(driver)
        actions = _make_actions(driver)
        assert actions.not_displayed_first_available([LOC_A, LOC_B]) is False

    def test_empty_list_returns_true(self) -> None:
        actions = _make_actions()
        assert actions.not_displayed_first_available([]) is True


class TestAssertNotDisplayedFirstAvailable:
    def test_passes_when_none_visible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        actions.assert_not_displayed_first_available([LOC_A, LOC_B])

    def test_raises_when_one_visible(self) -> None:
        driver = MagicMock()
        _visible_waiter(driver)
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="unexpectedly displayed"):
            actions.assert_not_displayed_first_available([LOC_A, LOC_B])

    def test_error_mentions_timeout(self) -> None:
        driver = MagicMock()
        _visible_waiter(driver)
        actions = _make_actions(driver, timeout=0.1)
        with pytest.raises(AssertionError, match=r"0\.1s"):
            actions.assert_not_displayed_first_available([LOC_A])
