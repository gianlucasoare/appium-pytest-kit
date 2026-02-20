"""Failure artifact capture helpers (screenshot + page source)."""


import re
import warnings
from pathlib import Path


def _safe_filename(node_id: str) -> str:
    """Convert a pytest node ID to a safe filesystem stem."""
    return re.sub(r"[^\w\-]", "_", node_id.replace("::", "__").replace("/", "_"))


def capture_screenshot(driver, node_id: str, artifacts_dir: Path) -> Path | None:
    """Save a PNG screenshot and return the path, or None on failure."""

    try:
        dest = artifacts_dir / "screenshots" / f"{_safe_filename(node_id)}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(dest))
        return dest
    except Exception as exc:
        warnings.warn(
            f"Failed to capture screenshot for {node_id!r}: {exc}",
            stacklevel=2,
        )
        return None


def capture_page_source(driver, node_id: str, artifacts_dir: Path) -> Path | None:
    """Save page source XML and return the path, or None on failure."""

    try:
        dest = artifacts_dir / "pagesource" / f"{_safe_filename(node_id)}.xml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(driver.page_source, encoding="utf-8")
        return dest
    except Exception as exc:
        warnings.warn(
            f"Failed to capture page source for {node_id!r}: {exc}",
            stacklevel=2,
        )
        return None


def attach_to_allure(path: Path, name: str, mime_type: str = "image/png") -> None:
    """Attach an artifact file to Allure report if allure-pytest is installed."""

    try:
        import allure  # type: ignore[import-untyped]

        with path.open("rb") as fh:
            allure.attach(fh.read(), name=name, attachment_type=mime_type)
    except (ImportError, OSError):
        pass
