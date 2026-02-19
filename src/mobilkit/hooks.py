"""Pytest hook specifications exposed by mobilkit."""

from __future__ import annotations

from typing import Any, Mapping

import pytest

from mobilkit.settings import MobilkitSettings


class MobilkitHookSpecs:
    """Custom hooks that extension packages can implement."""

    @pytest.hookspec(firstresult=True)
    def pytest_mobilkit_configure_settings(
        self,
        settings: MobilkitSettings,
    ) -> MobilkitSettings | None:
        """Return replacement settings to override the default load flow."""

    @pytest.hookspec
    def pytest_mobilkit_capabilities(
        self,
        capabilities: dict[str, Any],
        settings: MobilkitSettings,
    ) -> Mapping[str, Any] | None:
        """Return additional capabilities that will be merged into the driver config."""

    @pytest.hookspec
    def pytest_mobilkit_driver_created(
        self,
        driver: Any,
        settings: MobilkitSettings,
    ) -> None:
        """Observe driver creation for telemetry, wrappers, or custom setup."""
