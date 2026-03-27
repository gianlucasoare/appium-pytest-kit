"""Tests for visual regression module."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from appium_pytest_kit.visual import (
    BaselineManager,
    ScreenshotDiff,
    VisualRegressionError,
    assert_screenshot_match,
    compare_screenshots,
)


@pytest.fixture()
def _pillow_available():
    pytest.importorskip("PIL", reason="Pillow not installed")


@pytest.fixture()
def red_png(tmp_path, _pillow_available):
    """Create a 10x10 solid red PNG."""
    from PIL import Image

    img = Image.new("RGB", (10, 10), (255, 0, 0))
    path = tmp_path / "red.png"
    img.save(str(path))
    return path


@pytest.fixture()
def green_png(tmp_path, _pillow_available):
    """Create a 10x10 solid green PNG."""
    from PIL import Image

    img = Image.new("RGB", (10, 10), (0, 255, 0))
    path = tmp_path / "green.png"
    img.save(str(path))
    return path


@pytest.fixture()
def red_copy_png(tmp_path, red_png):
    """Create an identical copy of the red PNG."""
    path = tmp_path / "red_copy.png"
    shutil.copy2(str(red_png), str(path))
    return path


class TestVisualRegressionError:
    """Tests for VisualRegressionError."""

    def test_basic_message(self):
        err = VisualRegressionError("mismatch detected")
        assert "mismatch detected" in str(err)

    def test_includes_diff_and_threshold(self):
        err = VisualRegressionError(
            "mismatch",
            diff_ratio=0.05,
            threshold=0.01,
            baseline_path="/a/b.png",
            actual_path="/a/c.png",
        )
        assert "0.0500" in str(err)
        assert "0.0100" in str(err)
        assert err.baseline_path == "/a/b.png"
        assert err.actual_path == "/a/c.png"


class TestScreenshotDiff:
    """Tests for ScreenshotDiff dataclass."""

    def test_frozen(self):
        diff = ScreenshotDiff(match=True, diff_ratio=0.0, diff_pixels=0, total_pixels=100)
        with pytest.raises(AttributeError):
            diff.match = False  # type: ignore[misc]

    def test_fields(self):
        diff = ScreenshotDiff(
            match=False, diff_ratio=0.5, diff_pixels=50, total_pixels=100,
            diff_image_path=Path("/tmp/diff.png"),
        )
        assert not diff.match
        assert diff.diff_ratio == 0.5
        assert diff.diff_pixels == 50
        assert diff.diff_image_path == Path("/tmp/diff.png")


class TestCompareScreenshots:
    """Tests for compare_screenshots()."""

    def test_identical_images_match(self, red_png, red_copy_png):
        result = compare_screenshots(red_png, red_copy_png)

        assert result.match is True
        assert result.diff_ratio == 0.0
        assert result.diff_pixels == 0
        assert result.total_pixels == 100

    def test_different_images_mismatch(self, red_png, green_png):
        result = compare_screenshots(red_png, green_png, threshold=0.01)

        assert result.match is False
        assert result.diff_ratio == 1.0
        assert result.diff_pixels == 100

    def test_threshold_controls_match(self, red_png, green_png):
        result = compare_screenshots(red_png, green_png, threshold=1.0)

        assert result.match is True
        assert result.diff_ratio == 1.0

    def test_generates_diff_image(self, red_png, green_png, tmp_path):
        diff_path = tmp_path / "diff.png"
        result = compare_screenshots(
            red_png, green_png, diff_output_path=diff_path,
        )

        assert result.diff_image_path == diff_path
        assert diff_path.exists()

    def test_resizes_mismatched_dimensions(self, tmp_path, _pillow_available):
        from PIL import Image

        small = Image.new("RGB", (5, 5), (255, 0, 0))
        large = Image.new("RGB", (10, 10), (255, 0, 0))
        small_path = tmp_path / "small.png"
        large_path = tmp_path / "large.png"
        small.save(str(small_path))
        large.save(str(large_path))

        result = compare_screenshots(small_path, large_path)

        assert result.total_pixels == 25


class TestBaselineManager:
    """Tests for BaselineManager."""

    def test_baseline_path_without_platform(self, tmp_path):
        manager = BaselineManager(tmp_path)
        path = manager.baseline_path("tests::test_home::test_screen")

        assert path == tmp_path / "tests__test_home__test_screen.png"

    def test_baseline_path_with_platform(self, tmp_path):
        manager = BaselineManager(tmp_path)
        path = manager.baseline_path("tests::test_home", platform="android")

        assert path == tmp_path / "android" / "tests__test_home.png"

    def test_has_baseline_false(self, tmp_path):
        manager = BaselineManager(tmp_path)

        assert manager.has_baseline("nonexistent") is False

    def test_save_and_has_baseline(self, tmp_path, red_png):
        manager = BaselineManager(tmp_path / "baselines")
        manager.save_baseline("test_id", red_png, platform="android")

        assert manager.has_baseline("test_id", platform="android") is True
        saved = manager.baseline_path("test_id", platform="android")
        assert saved.exists()

    def test_save_refuses_overwrite_by_default(self, tmp_path, red_png):
        manager = BaselineManager(tmp_path / "baselines")
        manager.save_baseline("test_id", red_png)

        with pytest.raises(FileExistsError, match="already exists"):
            manager.save_baseline("test_id", red_png)

    def test_save_allows_overwrite(self, tmp_path, red_png, green_png):
        manager = BaselineManager(tmp_path / "baselines")
        manager.save_baseline("test_id", red_png)
        manager.save_baseline("test_id", green_png, overwrite=True)

        assert manager.has_baseline("test_id") is True


class TestAssertScreenshotMatch:
    """Tests for the high-level assert_screenshot_match() function."""

    def test_creates_baseline_on_first_run(self, tmp_path, _pillow_available):
        import base64

        from PIL import Image

        img = Image.new("RGB", (10, 10), (255, 0, 0))
        img_path = tmp_path / "temp.png"
        img.save(str(img_path))
        b64 = base64.b64encode(img_path.read_bytes()).decode()

        driver = MagicMock()
        driver.get_screenshot_as_base64.return_value = b64

        baselines = tmp_path / "baselines"
        artifacts = tmp_path / "artifacts"

        result = assert_screenshot_match(
            driver, "test::first", baselines, artifacts, platform="android",
        )

        assert result is None
        assert (baselines / "android" / "test__first.png").exists()

    def test_passes_on_identical_screenshot(self, tmp_path, _pillow_available):
        import base64

        from PIL import Image

        img = Image.new("RGB", (10, 10), (0, 128, 255))
        img_path = tmp_path / "temp.png"
        img.save(str(img_path))
        b64 = base64.b64encode(img_path.read_bytes()).decode()

        driver = MagicMock()
        driver.get_screenshot_as_base64.return_value = b64

        baselines = tmp_path / "baselines"
        artifacts = tmp_path / "artifacts"

        assert_screenshot_match(
            driver, "test::match", baselines, artifacts, platform="android",
        )

        result = assert_screenshot_match(
            driver, "test::match", baselines, artifacts, platform="android",
        )

        assert result is not None
        assert result.match is True

    def test_raises_on_mismatch(self, tmp_path, _pillow_available):
        import base64

        from PIL import Image

        red = Image.new("RGB", (10, 10), (255, 0, 0))
        green = Image.new("RGB", (10, 10), (0, 255, 0))

        red_path = tmp_path / "red.png"
        green_path = tmp_path / "green.png"
        red.save(str(red_path))
        green.save(str(green_path))

        baselines = tmp_path / "baselines"
        artifacts = tmp_path / "artifacts"

        manager = BaselineManager(baselines)
        manager.save_baseline("test::mismatch", red_path, platform="android")

        green_b64 = base64.b64encode(green_path.read_bytes()).decode()
        driver = MagicMock()
        driver.get_screenshot_as_base64.return_value = green_b64

        with pytest.raises(VisualRegressionError, match="mismatch"):
            assert_screenshot_match(
                driver, "test::mismatch", baselines, artifacts, platform="android",
            )

    def test_update_baselines_overwrites(self, tmp_path, _pillow_available):
        import base64

        from PIL import Image

        red = Image.new("RGB", (10, 10), (255, 0, 0))
        green = Image.new("RGB", (10, 10), (0, 255, 0))

        red_path = tmp_path / "red.png"
        green_path = tmp_path / "green.png"
        red.save(str(red_path))
        green.save(str(green_path))

        baselines = tmp_path / "baselines"
        artifacts = tmp_path / "artifacts"

        manager = BaselineManager(baselines)
        manager.save_baseline("test::update", red_path, platform="android")

        green_b64 = base64.b64encode(green_path.read_bytes()).decode()
        driver = MagicMock()
        driver.get_screenshot_as_base64.return_value = green_b64

        result = assert_screenshot_match(
            driver, "test::update", baselines, artifacts,
            platform="android", update_baselines=True,
        )

        assert result is None
