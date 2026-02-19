"""Public exception hierarchy for mobilkit."""

from __future__ import annotations


class MobilkitError(Exception):
    """Base exception for all framework-specific failures."""


class ConfigurationError(MobilkitError):
    """Raised when framework configuration is invalid."""


class WaitTimeoutError(MobilkitError):
    """Raised when an explicit wait condition does not pass in time."""


class ActionError(MobilkitError):
    """Raised when a high-level interaction action fails."""


class DriverCreationError(MobilkitError):
    """Raised when an Appium session cannot be created."""
