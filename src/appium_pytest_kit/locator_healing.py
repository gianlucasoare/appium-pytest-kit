"""Locator healing — fallback chains and strategy registry."""


import logging
from dataclasses import dataclass, field

from selenium.common.exceptions import NoSuchElementException, WebDriverException

from appium_pytest_kit.errors import ActionError
from appium_pytest_kit.waits import Locator

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class HealingResult:
    """Outcome of a locator healing attempt.

    Attributes:
        element: The found WebElement, or ``None`` if all locators failed.
        used_locator: The locator that succeeded, or ``None``.
        original_locator: The first locator in the chain (the "intended" one).
        healed: ``True`` if a fallback locator was used instead of the primary.
        attempts: Number of locators tried before success (or total if failed).
    """

    element: object
    used_locator: Locator | None
    original_locator: Locator
    healed: bool
    attempts: int


@dataclass
class LocatorChain:
    """An ordered list of fallback locators for a single UI element.

    The first locator is the primary (preferred) strategy. When ``find()``
    is called, each locator is tried in order until one succeeds.

    Example::

        login_btn = LocatorChain(
            ("accessibility id", "login_button"),
            ("id", "com.example.app:id/btn_login"),
            ("xpath", "//android.widget.Button[@text='Log in']"),
            name="login_button",
        )
        result = login_btn.find(driver)
        if result.healed:
            print(f"Primary locator broken, healed via {result.used_locator}")
    """

    primary: Locator
    fallbacks: tuple[Locator, ...] = ()
    name: str | None = None

    def __init__(
        self,
        primary: Locator,
        *fallbacks: Locator,
        name: str | None = None,
    ) -> None:
        self.primary = primary
        self.fallbacks = fallbacks
        self.name = name

    @property
    def all_locators(self) -> tuple[Locator, ...]:
        """All locators in priority order."""
        return (self.primary, *self.fallbacks)

    def find(self, driver) -> HealingResult:
        """Try each locator in order and return the first match.

        Args:
            driver: An Appium WebDriver instance.

        Returns:
            ``HealingResult`` with the found element and metadata.

        Raises:
            ActionError: If none of the locators find an element.
        """
        errors: list[str] = []

        for idx, locator in enumerate(self.all_locators):
            try:
                element = driver.find_element(*locator)
                healed = idx > 0
                label = self.name or str(self.primary)
                if healed:
                    logger.warning(
                        "locator:healed  name=%s  primary=%s  used=%s  attempt=%d",
                        label, self.primary, locator, idx + 1,
                    )
                else:
                    logger.debug("locator:found  name=%s  locator=%s", label, locator)
                return HealingResult(
                    element=element,
                    used_locator=locator,
                    original_locator=self.primary,
                    healed=healed,
                    attempts=idx + 1,
                )
            except (NoSuchElementException, WebDriverException) as exc:
                errors.append(f"{locator}: {exc}")
                continue

        label = self.name or str(self.primary)
        all_tried = ", ".join(str(loc) for loc in self.all_locators)
        msg = (
            f"All {len(self.all_locators)} locators failed for '{label}'. "
            f"Tried: {all_tried}"
        )
        raise ActionError(msg, locator=self.primary, action="find_with_healing")

    def find_or_none(self, driver) -> HealingResult:
        """Like ``find()`` but returns ``None`` element instead of raising."""
        try:
            return self.find(driver)
        except ActionError:
            return HealingResult(
                element=None,
                used_locator=None,
                original_locator=self.primary,
                healed=False,
                attempts=len(self.all_locators),
            )


@dataclass
class HealingRegistry:
    """Central registry for named locator chains.

    Register locators once, look them up by name in tests and page objects.
    Optionally track healing statistics across a test run.

    Example::

        registry = HealingRegistry()
        registry.register("login_btn", LocatorChain(
            ("accessibility id", "login_button"),
            ("id", "com.example.app:id/btn_login"),
            name="login_btn",
        ))

        chain = registry.get("login_btn")
        result = chain.find(driver)
    """

    _chains: dict[str, LocatorChain] = field(default_factory=dict, init=False)
    _heal_log: list[HealingResult] = field(default_factory=list, init=False)

    def register(self, name: str, chain: LocatorChain) -> None:
        """Register a locator chain under a name."""
        self._chains[name] = chain
        logger.debug("locator_registry:register  name=%s  count=%d", name, len(chain.all_locators))

    def register_simple(
        self,
        name: str,
        primary: Locator,
        *fallbacks: Locator,
    ) -> None:
        """Convenience: register a chain from raw locator tuples."""
        chain = LocatorChain(primary, *fallbacks, name=name)
        self.register(name, chain)

    def get(self, name: str) -> LocatorChain:
        """Look up a registered chain by name.

        Raises:
            KeyError: If the name is not registered.
        """
        if name not in self._chains:
            msg = f"No locator chain registered for {name!r}"
            raise KeyError(msg)
        return self._chains[name]

    def find(self, name: str, driver) -> HealingResult:
        """Look up a chain by name and find the element.

        Tracks healing statistics internally.
        """
        chain = self.get(name)
        result = chain.find(driver)
        if result.healed:
            self._heal_log.append(result)
        return result

    @property
    def registered_names(self) -> list[str]:
        """All registered chain names."""
        return sorted(self._chains.keys())

    @property
    def heal_count(self) -> int:
        """Number of times a fallback locator was used."""
        return len(self._heal_log)

    @property
    def heal_log(self) -> list[HealingResult]:
        """Copy of all healing events."""
        return list(self._heal_log)

    def summary(self) -> dict[str, int]:
        """Summary of healing statistics.

        Returns:
            Dict with keys ``total_heals``, ``unique_elements_healed``,
            ``registered_chains``.
        """
        unique = len({r.original_locator for r in self._heal_log})
        return {
            "total_heals": self.heal_count,
            "unique_elements_healed": unique,
            "registered_chains": len(self._chains),
        }

    def reset_log(self) -> None:
        """Clear the healing log (keeps registered chains)."""
        self._heal_log.clear()


def chain(primary: Locator, *fallbacks: Locator, name: str | None = None) -> LocatorChain:
    """Shorthand factory for creating a ``LocatorChain``.

    Example::

        from appium_pytest_kit.locator_healing import chain

        LOGIN_BTN = chain(
            ("accessibility id", "login_button"),
            ("id", "com.example.app:id/btn_login"),
            ("xpath", "//android.widget.Button[@text='Log in']"),
            name="login_button",
        )
    """
    return LocatorChain(primary, *fallbacks, name=name)
