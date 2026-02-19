"""Package version metadata."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

__all__ = ["__version__"]

try:
    __version__ = version("appium-pytest-kit")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
