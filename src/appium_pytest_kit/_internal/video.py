"""Screen recording lifecycle helpers."""


import base64
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from appium_pytest_kit._internal.diagnostics import _safe_filename

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from appium_pytest_kit.settings import AppiumPytestKitSettings


class ScreenRecorder:
    """Manages Appium screen recording start/stop lifecycle."""

    def start(self, driver, settings: "AppiumPytestKitSettings") -> None:
        """Begin recording if the platform/mode supports it."""

        if settings.platform == "ios" and settings.is_simulator:
            # iOS Simulator recording via Appium is not supported
            logger.debug("video:skip  iOS Simulator not supported")
            return
        try:
            driver.start_recording_screen()
            logger.info("video:started")
        except Exception:
            # Non-fatal: some environments / drivers don't support recording
            logger.debug("video:start_failed  driver may not support recording")

    def stop_and_save(
        self,
        driver,
        node_id: str,
        artifacts_dir: Path,
        settings: "AppiumPytestKitSettings",
    ) -> Path | None:
        """Stop recording, decode base64 payload, write MP4. Returns path or None."""

        if settings.platform == "ios" and settings.is_simulator:
            return None
        try:
            raw: str = driver.stop_recording_screen()
            if not raw:
                logger.debug("video:empty  no recording data returned")
                return None
            video_data = base64.b64decode(raw)
            dest = artifacts_dir / "videos" / f"{_safe_filename(node_id)}.mp4"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(video_data)
            logger.info("artifact:video  %s", dest)
            return dest
        except Exception:
            logger.debug("video:save_failed  could not save recording")
            return None
