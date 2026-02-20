"""Unit tests for MobileActions assertion methods."""

from unittest.mock import MagicMock

import pytest
from selenium.common.exceptions import NoSuchElementException

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


class TestIsNotDisplayed:
    def test_returns_true_when_element_invisible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        assert actions.is_not_displayed(LOC_A) is True

    def test_returns_false_when_element_visible(self) -> None:
        driver = MagicMock()
        _visible_waiter(driver)
        actions = _make_actions(driver)
        assert actions.is_not_displayed(LOC_A) is False

    def test_returns_true_when_element_absent_from_dom(self) -> None:
        driver = MagicMock()
        driver.find_element.side_effect = NoSuchElementException("gone")
        actions = _make_actions(driver)
        assert actions.is_not_displayed(LOC_A) is True


class TestAssertNotDisplayed:
    def test_passes_when_element_invisible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        actions.assert_not_displayed(LOC_A)

    def test_raises_when_element_visible(self) -> None:
        driver = MagicMock()
        _visible_waiter(driver)
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="still displayed"):
            actions.assert_not_displayed(LOC_A)

    def test_error_mentions_locator(self) -> None:
        driver = MagicMock()
        _visible_waiter(driver)
        actions = _make_actions(driver)
        with pytest.raises(AssertionError) as exc_info:
            actions.assert_not_displayed(LOC_A)
        assert "elementA" in str(exc_info.value)


class TestAssertText:
    def test_passes_on_exact_match(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.text = "Hello"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        actions.assert_text(LOC_A, "Hello")

    def test_raises_on_mismatch(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.text = "Goodbye"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="Text mismatch"):
            actions.assert_text(LOC_A, "Hello")

    def test_error_shows_expected_and_actual(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.text = "actual_value"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError) as exc_info:
            actions.assert_text(LOC_A, "expected_value")
        msg = str(exc_info.value)
        assert "expected_value" in msg
        assert "actual_value" in msg


class TestAssertTextContains:
    def test_passes_when_substring_present(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.text = "Welcome, testuser!"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        actions.assert_text_contains(LOC_A, "testuser")

    def test_raises_when_substring_absent(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.text = "Hello world"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="does not contain"):
            actions.assert_text_contains(LOC_A, "missing")

    def test_error_shows_partial_and_actual(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.text = "actual text"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError) as exc_info:
            actions.assert_text_contains(LOC_A, "missing_part")
        msg = str(exc_info.value)
        assert "missing_part" in msg
        assert "actual text" in msg


class TestAssertTextNotEmpty:
    def test_passes_when_text_present(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.text = "some text"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        actions.assert_text_not_empty(LOC_A)

    def test_raises_when_text_empty_string(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.text = ""
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="empty"):
            actions.assert_text_not_empty(LOC_A)

    def test_raises_when_text_whitespace_only(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.text = "   "
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="empty"):
            actions.assert_text_not_empty(LOC_A)


class TestAssertAttribute:
    def test_passes_on_exact_match(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.return_value = "true"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        actions.assert_attribute(LOC_A, "enabled", "true")

    def test_raises_on_mismatch(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.return_value = "false"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="Attribute"):
            actions.assert_attribute(LOC_A, "enabled", "true")

    def test_error_shows_attr_name_and_values(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.return_value = "actual_val"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError) as exc_info:
            actions.assert_attribute(LOC_A, "content-desc", "expected_val")
        msg = str(exc_info.value)
        assert "content-desc" in msg
        assert "expected_val" in msg
        assert "actual_val" in msg


class TestIsEnabled:
    def test_returns_true_when_element_enabled(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.is_enabled.return_value = True
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        assert actions.is_enabled(LOC_A) is True

    def test_returns_false_when_element_disabled(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.is_enabled.return_value = False
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        assert actions.is_enabled(LOC_A) is False

    def test_returns_false_when_not_visible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        assert actions.is_enabled(LOC_A) is False


class TestAssertEnabled:
    def test_passes_when_enabled(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.is_enabled.return_value = True
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        actions.assert_enabled(LOC_A)

    def test_raises_when_disabled(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.is_enabled.return_value = False
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="not enabled"):
            actions.assert_enabled(LOC_A)


class TestAssertNotEnabled:
    def test_passes_when_disabled(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.is_enabled.return_value = False
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        actions.assert_not_enabled(LOC_A)

    def test_raises_when_enabled(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.is_enabled.return_value = True
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="enabled"):
            actions.assert_not_enabled(LOC_A)

    def test_passes_when_not_visible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        # not visible → treated as not enabled → should pass
        actions.assert_not_enabled(LOC_A)


class TestIsChecked:
    def test_returns_true_for_checked_attribute(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.side_effect = lambda attr: "true" if attr == "checked" else None
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        assert actions.is_checked(LOC_A) is True

    def test_returns_true_for_selected_attribute(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.side_effect = lambda attr: ("true" if attr == "selected" else None)
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        assert actions.is_checked(LOC_A) is True

    def test_returns_false_when_unchecked(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.return_value = "false"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        assert actions.is_checked(LOC_A) is False

    def test_returns_false_when_not_visible(self) -> None:
        driver = MagicMock()
        _invisible_waiter(driver)
        actions = _make_actions(driver)
        assert actions.is_checked(LOC_A) is False


class TestAssertChecked:
    def test_passes_when_checked(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.side_effect = lambda attr: "true" if attr == "checked" else None
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        actions.assert_checked(LOC_A)

    def test_raises_when_unchecked(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.return_value = "false"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="not checked"):
            actions.assert_checked(LOC_A)


class TestAssertNotChecked:
    def test_passes_when_unchecked(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.return_value = "false"
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        actions.assert_not_checked(LOC_A)

    def test_raises_when_checked(self) -> None:
        driver = MagicMock()
        el = MagicMock()
        el.is_displayed.return_value = True
        el.get_attribute.side_effect = lambda attr: "true" if attr == "checked" else None
        driver.find_element.return_value = el
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="checked"):
            actions.assert_not_checked(LOC_A)


class TestCount:
    def test_returns_count_of_matching_elements(self) -> None:
        driver = MagicMock()
        driver.find_elements.return_value = [MagicMock(), MagicMock(), MagicMock()]
        actions = _make_actions(driver)
        assert actions.count(LOC_A) == 3

    def test_returns_zero_when_no_elements(self) -> None:
        driver = MagicMock()
        driver.find_elements.return_value = []
        actions = _make_actions(driver)
        assert actions.count(LOC_A) == 0


class TestAssertCount:
    def test_passes_when_count_matches(self) -> None:
        driver = MagicMock()
        driver.find_elements.return_value = [MagicMock(), MagicMock()]
        actions = _make_actions(driver)
        actions.assert_count(LOC_A, 2)

    def test_raises_when_count_differs(self) -> None:
        driver = MagicMock()
        driver.find_elements.return_value = [MagicMock()]
        actions = _make_actions(driver)
        with pytest.raises(AssertionError, match="count mismatch"):
            actions.assert_count(LOC_A, 3)

    def test_error_shows_expected_and_actual(self) -> None:
        driver = MagicMock()
        driver.find_elements.return_value = [MagicMock(), MagicMock()]
        actions = _make_actions(driver)
        with pytest.raises(AssertionError) as exc_info:
            actions.assert_count(LOC_A, 5)
        msg = str(exc_info.value)
        assert "5" in msg
        assert "2" in msg
