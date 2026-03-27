"""Visual regression testing — screenshot comparison with baseline management."""


import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from appium_pytest_kit.errors import AppiumPytestKitError

logger = logging.getLogger(__name__)


class VisualRegressionError(AppiumPytestKitError):
    """Raised when a screenshot does not match its baseline."""

    def __init__(
        self,
        message: str = "Visual regression detected",
        *,
        baseline_path: str | None = None,
        actual_path: str | None = None,
        diff_ratio: float | None = None,
        threshold: float | None = None,
    ) -> None:
        self.baseline_path = baseline_path
        self.actual_path = actual_path
        self.diff_ratio = diff_ratio
        self.threshold = threshold

        parts = [message]
        if diff_ratio is not None and threshold is not None:
            parts.append(f"diff={diff_ratio:.4f} threshold={threshold:.4f}")
        super().__init__(" ".join(parts))


@dataclass(frozen=True, slots=True)
class ScreenshotDiff:
    """Result of comparing two screenshots."""

    match: bool
    diff_ratio: float
    diff_pixels: int
    total_pixels: int
    diff_image_path: Path | None = None


def _ensure_pillow():
    try:
        from PIL import Image

        return Image
    except ImportError as exc:
        msg = (
            "Pillow is required for visual regression testing. "
            "Install it with: pip install appium-pytest-kit[visual]"
        )
        raise ImportError(msg) from exc


def compare_screenshots(
    actual_path: str | Path,
    baseline_path: str | Path,
    *,
    threshold: float = 0.01,
    diff_output_path: str | Path | None = None,
) -> ScreenshotDiff:
    """Compare two screenshot images and return a diff result.

    Parameters
    ----------
    actual_path:
        Path to the current screenshot.
    baseline_path:
        Path to the reference baseline image.
    threshold:
        Maximum allowed ratio of differing pixels (0.0-1.0).
        Default 0.01 means 1% tolerance.
    diff_output_path:
        Optional path to save a diff image highlighting differences.

    Returns
    -------
    ScreenshotDiff
        Comparison result with match status and metrics.
    """
    Image = _ensure_pillow()

    actual = Image.open(str(actual_path)).convert("RGB")
    baseline = Image.open(str(baseline_path)).convert("RGB")

    if actual.size != baseline.size:
        baseline = baseline.resize(actual.size, Image.LANCZOS)
        logger.warning(
            "visual:resize  baseline resized from original to %s to match actual",
            actual.size,
        )

    _get_pixels = getattr(Image.Image, "get_flattened_data", None) or Image.Image.getdata
    actual_pixels = list(_get_pixels(actual))
    baseline_pixels = list(_get_pixels(baseline))
    total = len(actual_pixels)

    diff_count = sum(1 for a, b in zip(actual_pixels, baseline_pixels, strict=False) if a != b)
    diff_ratio = diff_count / total if total > 0 else 0.0

    diff_image_path = None
    if diff_output_path is not None:
        diff_image = Image.new("RGB", actual.size)
        diff_data = []
        for a, b in zip(actual_pixels, baseline_pixels, strict=False):
            if a != b:
                diff_data.append((255, 0, 0))
            else:
                r, g, bl = a
                grey = (r + g + bl) // 3
                diff_data.append((grey, grey, grey))
        diff_image.putdata(diff_data)
        out_path = Path(diff_output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        diff_image.save(str(out_path))
        diff_image_path = out_path

    is_match = diff_ratio <= threshold

    logger.info(
        "visual:compare  match=%s  diff=%.4f  threshold=%.4f  pixels=%d/%d",
        is_match, diff_ratio, threshold, diff_count, total,
    )

    return ScreenshotDiff(
        match=is_match,
        diff_ratio=diff_ratio,
        diff_pixels=diff_count,
        total_pixels=total,
        diff_image_path=diff_image_path,
    )


class BaselineManager:
    """Manage visual regression baselines on the filesystem.

    Parameters
    ----------
    baselines_dir:
        Root directory for baseline images.
        Default layout: ``baselines_dir/{platform}/{test_id}.png``
    """

    def __init__(self, baselines_dir: str | Path) -> None:
        self._root = Path(baselines_dir)

    def baseline_path(
        self,
        test_id: str,
        *,
        platform: str | None = None,
    ) -> Path:
        """Return the expected filesystem path for a baseline image."""
        safe_id = test_id.replace("::", "__").replace("/", "_")
        if platform:
            return self._root / platform / f"{safe_id}.png"
        return self._root / f"{safe_id}.png"

    def has_baseline(
        self,
        test_id: str,
        *,
        platform: str | None = None,
    ) -> bool:
        """Check whether a baseline exists for the given test."""
        return self.baseline_path(test_id, platform=platform).exists()

    def save_baseline(
        self,
        test_id: str,
        screenshot_path: str | Path,
        *,
        platform: str | None = None,
        overwrite: bool = False,
    ) -> Path:
        """Copy a screenshot to become the new baseline.

        Returns the path where the baseline was saved.
        """
        dest = self.baseline_path(test_id, platform=platform)
        if dest.exists() and not overwrite:
            msg = (
                f"Baseline already exists at {dest}. "
                "Pass overwrite=True to replace it."
            )
            raise FileExistsError(msg)

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(screenshot_path), str(dest))
        logger.info("visual:baseline_saved  test=%s  path=%s", test_id, dest)
        return dest


def assert_screenshot_match(
    driver: Any,
    test_id: str,
    baselines_dir: str | Path,
    artifacts_dir: str | Path,
    *,
    platform: str | None = None,
    threshold: float = 0.01,
    update_baselines: bool = False,
) -> ScreenshotDiff | None:
    """Capture a screenshot, compare to baseline, and raise on mismatch.

    Parameters
    ----------
    driver:
        Appium WebDriver instance.
    test_id:
        Unique test identifier (typically ``request.node.nodeid``).
    baselines_dir:
        Root directory for baseline images.
    artifacts_dir:
        Directory to save actual screenshots and diff images.
    platform:
        Platform name for baseline lookup (``"android"`` or ``"ios"``).
    threshold:
        Maximum allowed pixel diff ratio (0.0-1.0).
    update_baselines:
        If True, save/overwrite the baseline instead of comparing.

    Returns
    -------
    ScreenshotDiff | None
        Comparison result, or None when updating baselines.

    Raises
    ------
    VisualRegressionError
        When the diff exceeds the threshold and ``update_baselines`` is False.
    """
    manager = BaselineManager(baselines_dir)
    safe_id = test_id.replace("::", "__").replace("/", "_")

    actual_dir = Path(artifacts_dir) / "screenshots" / "visual"
    actual_dir.mkdir(parents=True, exist_ok=True)
    actual_path = actual_dir / f"{safe_id}.png"

    screenshot_base64 = driver.get_screenshot_as_base64()
    import base64

    actual_path.write_bytes(base64.b64decode(screenshot_base64))
    logger.debug("visual:captured  path=%s", actual_path)

    if update_baselines:
        manager.save_baseline(test_id, actual_path, platform=platform, overwrite=True)
        return None

    baseline = manager.baseline_path(test_id, platform=platform)
    if not baseline.exists():
        manager.save_baseline(test_id, actual_path, platform=platform)
        logger.info("visual:new_baseline  test=%s  path=%s", test_id, baseline)
        return None

    diff_path = actual_dir / f"{safe_id}_diff.png"
    result = compare_screenshots(
        actual_path, baseline, threshold=threshold, diff_output_path=diff_path,
    )

    if not result.match:
        raise VisualRegressionError(
            f"Screenshot mismatch for {test_id}",
            baseline_path=str(baseline),
            actual_path=str(actual_path),
            diff_ratio=result.diff_ratio,
            threshold=threshold,
        )

    return result
