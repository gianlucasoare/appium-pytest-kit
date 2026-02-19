"""Pytest hook specifications exposed by appium-pytest-kit."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from appium_pytest_kit.settings import AppiumPytestKitSettings


class AppiumPytestKitHookSpecs:
    """Custom hooks that extension packages can implement."""

    @pytest.hookspec(firstresult=True)
    def pytest_appium_pytest_kit_configure_settings(
        self,
        settings: AppiumPytestKitSettings,
    ) -> AppiumPytestKitSettings | None:
        """Return replacement settings to override the default load flow."""

    @pytest.hookspec
    def pytest_appium_pytest_kit_capabilities(
        self,
        capabilities: dict[str, Any],
        settings: AppiumPytestKitSettings,
    ) -> Mapping[str, Any] | None:
        """Return additional capabilities that will be merged into the driver config."""

    @pytest.hookspec
    def pytest_appium_pytest_kit_driver_created(
        self,
        driver: Any,
        settings: AppiumPytestKitSettings,
    ) -> None:
        """Observe driver creation for telemetry, wrappers, or custom setup."""
