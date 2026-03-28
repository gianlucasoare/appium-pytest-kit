"""Soft assertions — collect multiple failures in one test."""


import logging
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field

from appium_pytest_kit.errors import AppiumPytestKitError

logger = logging.getLogger(__name__)


class SoftAssertionError(AppiumPytestKitError):
    """Raised when one or more soft assertions fail at checkpoint or context exit.

    Attributes:
        failures: list of individual ``AssertionFailure`` records.
    """

    def __init__(self, failures: list["AssertionFailure"]) -> None:
        self.failures = list(failures)
        self.failure_count = len(self.failures)
        count = len(self.failures)
        lines = [f"{count} soft assertion(s) failed:"]
        for idx, f in enumerate(self.failures, 1):
            prefix = f"  [{idx}]"
            if f.label:
                prefix = f"{prefix} ({f.label})"
            lines.append(f"{prefix} {f.message}")
            if f.expected is not None or f.actual is not None:
                lines.append(f"        expected={f.expected!r}  actual={f.actual!r}")
        super().__init__("\n".join(lines))


@dataclass(frozen=True, slots=True)
class AssertionFailure:
    """Record of a single failed soft assertion."""

    message: str
    label: str | None = None
    expected: object = None
    actual: object = None


@dataclass
class SoftAssert:
    """Collector for soft assertions.

    Use as a context manager or call ``checkpoint()`` explicitly to raise
    ``SoftAssertionError`` when any recorded check has failed.

    Example::

        soft = SoftAssert()
        soft.check(title == "Home", "title should be Home", expected="Home", actual=title)
        soft.check(count > 0, "items should be non-empty")
        soft.assert_all()  # raises SoftAssertionError if any check failed
    """

    _failures: list[AssertionFailure] = field(default_factory=list, init=False)

    # -- core API --------------------------------------------------------

    def check(
        self,
        condition: bool,
        message: str = "Assertion failed",
        *,
        label: str | None = None,
        expected: object = None,
        actual: object = None,
    ) -> None:
        """Record an assertion without stopping the test.

        Args:
            condition: ``True`` means pass; ``False`` records a failure.
            message: Human-readable failure description.
            label: Optional short tag (e.g. ``"username_field"``).
            expected: Expected value (for reporting).
            actual: Actual value (for reporting).
        """
        if condition:
            return
        failure = AssertionFailure(
            message=message,
            label=label,
            expected=expected,
            actual=actual,
        )
        self._failures.append(failure)
        logger.debug("soft_assert:fail  label=%s  message=%s", label, message)

    def check_equal(
        self,
        actual: object,
        expected: object,
        message: str | None = None,
        *,
        label: str | None = None,
    ) -> None:
        """Shorthand: assert ``actual == expected``."""
        msg = message or f"Expected {expected!r}, got {actual!r}"
        self.check(actual == expected, msg, label=label, expected=expected, actual=actual)

    def check_true(
        self,
        value: object,
        message: str = "Expected truthy value",
        *,
        label: str | None = None,
    ) -> None:
        """Shorthand: assert ``bool(value)`` is ``True``."""
        self.check(bool(value), message, label=label, expected=True, actual=value)

    def check_false(
        self,
        value: object,
        message: str = "Expected falsy value",
        *,
        label: str | None = None,
    ) -> None:
        """Shorthand: assert ``bool(value)`` is ``False``."""
        self.check(not bool(value), message, label=label, expected=False, actual=value)

    def check_in(
        self,
        member: object,
        container: object,
        message: str | None = None,
        *,
        label: str | None = None,
    ) -> None:
        """Shorthand: assert ``member in container``."""
        msg = message or f"Expected {member!r} in {container!r}"
        self.check(member in container, msg, label=label, expected=member, actual=container)  # type: ignore[operator]

    def check_not_none(
        self,
        value: object,
        message: str = "Expected non-None value",
        *,
        label: str | None = None,
    ) -> None:
        """Shorthand: assert ``value is not None``."""
        self.check(value is not None, message, label=label, expected="not None", actual=value)

    def check_gt(
        self,
        actual: object,
        threshold: object,
        message: str | None = None,
        *,
        label: str | None = None,
    ) -> None:
        """Shorthand: assert ``actual > threshold``."""
        msg = message or f"Expected {actual!r} > {threshold!r}"
        self.check(actual > threshold, msg, label=label, expected=f"> {threshold!r}", actual=actual)  # type: ignore[operator]

    def check_lt(
        self,
        actual: object,
        threshold: object,
        message: str | None = None,
        *,
        label: str | None = None,
    ) -> None:
        """Shorthand: assert ``actual < threshold``."""
        msg = message or f"Expected {actual!r} < {threshold!r}"
        self.check(actual < threshold, msg, label=label, expected=f"< {threshold!r}", actual=actual)  # type: ignore[operator]

    def check_contains(
        self,
        haystack: str,
        needle: str,
        message: str | None = None,
        *,
        label: str | None = None,
    ) -> None:
        """Shorthand: assert ``needle in haystack`` for strings."""
        msg = message or f"Expected {haystack!r} to contain {needle!r}"
        self.check(needle in haystack, msg, label=label, expected=needle, actual=haystack)

    # -- inspection ------------------------------------------------------

    @property
    def failures(self) -> list[AssertionFailure]:
        """Return a copy of recorded failures."""
        return list(self._failures)

    @property
    def failed(self) -> bool:
        """Return ``True`` if any soft assertion has failed."""
        return len(self._failures) > 0

    @property
    def failure_count(self) -> int:
        """Return the number of recorded failures."""
        return len(self._failures)

    # -- flush / checkpoint ----------------------------------------------

    def assert_all(self) -> None:
        """Raise ``SoftAssertionError`` if any soft assertion failed, then reset."""
        if not self._failures:
            return
        failures = list(self._failures)
        self._failures.clear()
        raise SoftAssertionError(failures)

    def reset(self) -> None:
        """Discard all recorded failures without raising."""
        self._failures.clear()


@contextmanager
def soft_assertions() -> Generator[SoftAssert, None, None]:
    """Context manager that collects soft assertions and raises at exit.

    Example::

        with soft_assertions() as sa:
            sa.check_equal(title, "Home", label="title")
            sa.check_true(is_visible, label="welcome_banner")
            sa.check_contains(subtitle, "Hello", label="greeting")
        # SoftAssertionError raised here if anything failed
    """
    collector = SoftAssert()
    yield collector
    collector.assert_all()
