"""Extension contracts for customizing appium-pytest-kit behavior."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from appium_pytest_kit.driver import DriverConfig
    from appium_pytest_kit.settings import AppiumPytestKitSettings


@runtime_checkable
class CapabilitiesAdapter(Protocol):
    """Contract for mutating/augmenting desired capabilities."""

    def adapt(
        self,
        capabilities: Mapping[str, Any],
        settings: AppiumPytestKitSettings,
    ) -> Mapping[str, Any]:
        """Return a new mapping containing adapted capabilities."""


@runtime_checkable
class DriverFactory(Protocol):
    """Contract for creating a concrete driver from a driver config."""

    def __call__(self, config: DriverConfig) -> Any:
        """Instantiate and return a driver client."""
