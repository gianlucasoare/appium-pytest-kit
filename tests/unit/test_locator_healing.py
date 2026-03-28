"""Tests for the locator healing module."""

from unittest.mock import MagicMock

import pytest
from selenium.common.exceptions import NoSuchElementException

from appium_pytest_kit.errors import ActionError
from appium_pytest_kit.locator_healing import (
    HealingRegistry,
    LocatorChain,
    chain,
)


def _mock_driver(*found_locators):
    """Create a mock driver that finds elements for specific locators.

    Args:
        *found_locators: locator tuples that should succeed.
            All other locators raise NoSuchElementException.
    """
    driver = MagicMock()
    found_set = set(found_locators)

    def find_element(by, value):
        if (by, value) in found_set:
            elem = MagicMock()
            elem.text = f"found:{by}={value}"
            return elem
        raise NoSuchElementException(f"No element: ({by}, {value})")

    driver.find_element.side_effect = find_element
    return driver


class TestLocatorChain:
    """LocatorChain find behavior."""

    def test_primary_found_returns_not_healed(self) -> None:
        primary = ("id", "btn_login")
        lc = LocatorChain(primary, name="login")
        driver = _mock_driver(primary)

        result = lc.find(driver)

        assert result.element is not None
        assert result.used_locator == primary
        assert result.original_locator == primary
        assert result.healed is False
        assert result.attempts == 1

    def test_fallback_used_when_primary_fails(self) -> None:
        primary = ("id", "btn_login")
        fallback = ("accessibility id", "login_button")
        lc = LocatorChain(primary, fallback, name="login")
        driver = _mock_driver(fallback)

        result = lc.find(driver)

        assert result.element is not None
        assert result.used_locator == fallback
        assert result.original_locator == primary
        assert result.healed is True
        assert result.attempts == 2

    def test_second_fallback_used(self) -> None:
        primary = ("id", "gone")
        fb1 = ("id", "also_gone")
        fb2 = ("xpath", "//button")
        lc = LocatorChain(primary, fb1, fb2, name="element")
        driver = _mock_driver(fb2)

        result = lc.find(driver)

        assert result.healed is True
        assert result.used_locator == fb2
        assert result.attempts == 3

    def test_all_fail_raises_action_error(self) -> None:
        primary = ("id", "missing1")
        fb = ("id", "missing2")
        lc = LocatorChain(primary, fb, name="gone_element")
        driver = _mock_driver()  # nothing found

        with pytest.raises(ActionError, match="All 2 locators failed"):
            lc.find(driver)

    def test_find_or_none_returns_none_element(self) -> None:
        primary = ("id", "missing")
        lc = LocatorChain(primary, name="optional")
        driver = _mock_driver()

        result = lc.find_or_none(driver)

        assert result.element is None
        assert result.used_locator is None
        assert result.healed is False
        assert result.attempts == 1

    def test_find_or_none_returns_element_on_success(self) -> None:
        primary = ("id", "exists")
        lc = LocatorChain(primary, name="found")
        driver = _mock_driver(primary)

        result = lc.find_or_none(driver)

        assert result.element is not None

    def test_all_locators_property(self) -> None:
        primary = ("id", "a")
        fb1 = ("id", "b")
        fb2 = ("id", "c")
        lc = LocatorChain(primary, fb1, fb2)

        assert lc.all_locators == (("id", "a"), ("id", "b"), ("id", "c"))

    def test_chain_name_attribute(self) -> None:
        lc = LocatorChain(("id", "x"), name="my_element")
        assert lc.name == "my_element"

    def test_chain_without_name(self) -> None:
        lc = LocatorChain(("id", "x"))
        assert lc.name is None


class TestHealingRegistry:
    """Registry for named locator chains."""

    def test_register_and_get(self) -> None:
        registry = HealingRegistry()
        lc = LocatorChain(("id", "btn"), name="button")
        registry.register("button", lc)

        retrieved = registry.get("button")

        assert retrieved is lc

    def test_register_simple(self) -> None:
        registry = HealingRegistry()
        registry.register_simple(
            "login",
            ("id", "btn_login"),
            ("accessibility id", "login_button"),
        )

        lc = registry.get("login")

        assert lc.name == "login"
        assert len(lc.all_locators) == 2

    def test_get_missing_raises_key_error(self) -> None:
        registry = HealingRegistry()

        with pytest.raises(KeyError, match="unregistered"):
            registry.get("unregistered")

    def test_find_tracks_healing(self) -> None:
        registry = HealingRegistry()
        primary = ("id", "gone")
        fallback = ("id", "found")
        registry.register_simple("element", primary, fallback)

        driver = _mock_driver(fallback)
        result = registry.find("element", driver)

        assert result.healed is True
        assert registry.heal_count == 1

    def test_find_no_healing_not_tracked(self) -> None:
        registry = HealingRegistry()
        primary = ("id", "found")
        registry.register_simple("element", primary)

        driver = _mock_driver(primary)
        registry.find("element", driver)

        assert registry.heal_count == 0

    def test_registered_names(self) -> None:
        registry = HealingRegistry()
        registry.register_simple("btn_a", ("id", "a"))
        registry.register_simple("btn_b", ("id", "b"))

        assert registry.registered_names == ["btn_a", "btn_b"]

    def test_summary(self) -> None:
        registry = HealingRegistry()
        registry.register_simple("elem", ("id", "gone"), ("id", "found"))
        driver = _mock_driver(("id", "found"))
        registry.find("elem", driver)

        summary = registry.summary()

        assert summary["total_heals"] == 1
        assert summary["unique_elements_healed"] == 1
        assert summary["registered_chains"] == 1

    def test_reset_log_keeps_chains(self) -> None:
        registry = HealingRegistry()
        registry.register_simple("elem", ("id", "gone"), ("id", "found"))
        driver = _mock_driver(("id", "found"))
        registry.find("elem", driver)

        registry.reset_log()

        assert registry.heal_count == 0
        assert len(registry.registered_names) == 1

    def test_heal_log_returns_copy(self) -> None:
        registry = HealingRegistry()
        log1 = registry.heal_log
        log2 = registry.heal_log
        assert log1 is not log2


class TestChainFactory:
    """The ``chain()`` shorthand factory."""

    def test_creates_locator_chain(self) -> None:
        lc = chain(
            ("id", "primary"),
            ("id", "fallback1"),
            ("id", "fallback2"),
            name="my_element",
        )

        assert isinstance(lc, LocatorChain)
        assert lc.primary == ("id", "primary")
        assert len(lc.fallbacks) == 2
        assert lc.name == "my_element"

    def test_single_locator_chain(self) -> None:
        lc = chain(("id", "only"))

        assert lc.primary == ("id", "only")
        assert lc.fallbacks == ()
