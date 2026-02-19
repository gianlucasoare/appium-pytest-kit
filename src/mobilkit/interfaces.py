"""Extension contracts for customizing mobilkit behavior."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol, runtime_checkable

if TYPE_CHECKING:
    from mobilkit.driver import DriverConfig
    from mobilkit.settings import MobilkitSettings


@runtime_checkable
class CapabilitiesAdapter(Protocol):
    """Contract for mutating/augmenting desired capabilities."""

    def adapt(
        self,
        capabilities: Mapping[str, Any],
        settings: "MobilkitSettings",
    ) -> Mapping[str, Any]:
        """Return a new mapping containing adapted capabilities."""


@runtime_checkable
class DriverFactory(Protocol):
    """Contract for creating a concrete driver from a driver config."""

    def __call__(self, config: "DriverConfig") -> Any:
        """Instantiate and return a driver client."""
