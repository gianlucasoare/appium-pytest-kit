"""Screen recording lifecycle helpers."""


import base64
from pathlib import Path
from typing import TYPE_CHECKING

from appium_pytest_kit._internal.diagnostics import _safe_filename

if TYPE_CHECKING:
    from appium_pytest_kit.settings import AppiumPytestKitSettings


class ScreenRecorder:
    """Manages Appium screen recording start/stop lifecycle."""

    def start(self, driver, settings: "AppiumPytestKitSettings") -> None:
        """Begin recording if the platform/mode supports it."""

        if settings.platform == "ios" and settings.is_simulator:
            # iOS Simulator recording via Appium is not supported
            return
        try:
            driver.start_recording_screen()
        except Exception:
            # Non-fatal: some environments / drivers don't support recording
            pass

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
                return None
            video_data = base64.b64decode(raw)
            dest = artifacts_dir / "videos" / f"{_safe_filename(node_id)}.mp4"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(video_data)
            return dest
        except Exception:
            return None
