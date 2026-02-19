"""Public exception hierarchy for appium-pytest-kit."""

from __future__ import annotations


class AppiumPytestKitError(Exception):
    """Base exception for all framework-specific failures."""


class ConfigurationError(AppiumPytestKitError):
    """Raised when framework configuration is invalid."""


class WaitTimeoutError(AppiumPytestKitError):
    """Raised when an explicit wait condition does not pass in time."""


class ActionError(AppiumPytestKitError):
    """Raised when a high-level interaction action fails."""


class DriverCreationError(AppiumPytestKitError):
    """Raised when an Appium session cannot be created."""
