"""Public exception hierarchy for appium-pytest-kit."""


def _fmt_locator(locator: tuple[str, str] | None) -> str:
    if locator is None:
        return ""
    by, value = locator
    return f" [{by}={value!r}]"


class AppiumPytestKitError(Exception):
    """Base exception for all framework-specific failures."""


class ConfigurationError(AppiumPytestKitError):
    """Raised when framework configuration is invalid."""


class DeviceResolutionError(AppiumPytestKitError):
    """Raised when a target device cannot be resolved."""


class LaunchValidationError(AppiumPytestKitError):
    """Raised when the app launch configuration is incomplete."""


class WaitTimeoutError(AppiumPytestKitError):
    """Raised when an explicit wait condition does not pass in time."""

    def __init__(
        self,
        message: str = "Explicit wait timed out",
        *,
        locator: tuple[str, str] | None = None,
        timeout: float | None = None,
    ) -> None:
        self.locator = locator
        self.timeout = timeout
        detail = message + _fmt_locator(locator)
        if timeout is not None:
            detail = f"{detail} (timeout={timeout}s)"
        super().__init__(detail)


class ActionError(AppiumPytestKitError):
    """Raised when a high-level interaction action fails."""

    def __init__(
        self,
        message: str = "Action failed",
        *,
        locator: tuple[str, str] | None = None,
        action: str | None = None,
    ) -> None:
        self.locator = locator
        self.action = action
        detail = message + _fmt_locator(locator)
        if action is not None:
            detail = f"[{action}] {detail}"
        super().__init__(detail)


class DriverCreationError(AppiumPytestKitError):
    """Raised when an Appium session cannot be created."""
