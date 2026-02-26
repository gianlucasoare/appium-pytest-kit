"""3-tier device resolution: explicit settings → devices.yaml → auto-detect."""


import json
import logging
import re
import subprocess
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from appium_pytest_kit.errors import ConfigurationError

logger = logging.getLogger(__name__)
_IOS_UDID_RE = re.compile(
    r"^(?:[0-9A-Fa-f]{40}|[0-9A-Fa-f]{8}(?:-[0-9A-Fa-f]{4}){3}-[0-9A-Fa-f]{12})$"
)

if TYPE_CHECKING:
    from appium_pytest_kit.settings import AppiumPytestKitSettings


@dataclass(frozen=True, slots=True)
class DeviceInfo:
    """Resolved device properties used to build capabilities."""

    device_name: str
    platform_name: str
    udid: str | None = None
    platform_version: str | None = None
    automation_name: str | None = None
    is_simulator: bool = False


class DeviceResolver:
    """Resolves a target device through 3-tier priority."""

    def __init__(self, settings: "AppiumPytestKitSettings") -> None:
        self._settings = settings

    def resolve(self) -> DeviceInfo | None:
        """Return DeviceInfo from first applicable tier, or None.

        Priority:
        1. Explicit env/CLI (device_name or udid is set)
        2. devices.yaml profile (device_profile is set)
        3. Auto-detect via adb (Android) or xcrun (iOS)
        """
        s = self._settings
        logger.info("device:resolving  platform=%s", s.platform)

        if s.device_name or s.udid:
            info = self._from_explicit()
            logger.info(
                "device:tier-1 (explicit)  name=%r  udid=%s  version=%s",
                info.device_name, info.udid or "—", info.platform_version or "—",
            )
            return info

        if s.device_profile:
            info = self._from_yaml()
            logger.info(
                "device:tier-2 (profile=%r)  name=%r  udid=%s",
                s.device_profile, info.device_name, info.udid or "—",
            )
            return info

        info = self._auto_detect()
        if info:
            logger.info(
                "device:tier-3 (auto-detect)  name=%r  udid=%s  version=%s",
                info.device_name, info.udid or "—", info.platform_version or "—",
            )
        else:
            logger.info("device:tier-3 (auto-detect)  no device found")
        return info

    # ------------------------------------------------------------------
    # Tier 1 - explicit settings
    # ------------------------------------------------------------------

    def _from_explicit(self) -> DeviceInfo:
        s = self._settings
        return DeviceInfo(
            device_name=s.device_name or "Unknown",
            platform_name=s.platform,
            udid=s.udid,
            platform_version=s.platform_version,
            automation_name=s.automation_name,
            is_simulator=s.is_simulator,
        )

    # ------------------------------------------------------------------
    # Tier 2 - devices.yaml profile
    # ------------------------------------------------------------------

    def _from_yaml(self) -> DeviceInfo:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            msg = "PyYAML is required for device profiles. Install with: pip install PyYAML"
            raise ConfigurationError(msg) from exc

        devices_yaml = Path(self._settings.devices_yaml)
        if not devices_yaml.exists():
            msg = f"devices.yaml not found at {devices_yaml}"
            raise ConfigurationError(msg)

        with devices_yaml.open(encoding="utf-8") as fh:
            data: dict[str, Any] = yaml.safe_load(fh) or {}

        profile = self._settings.device_profile
        devices: dict[str, Any] = data.get("devices", {})
        if profile not in devices:
            available = list(devices.keys())
            msg = (
                f"Device profile {profile!r} not found in {devices_yaml}. "
                f"Available: {available}"
            )
            raise ConfigurationError(msg)

        entry = devices[profile]
        return DeviceInfo(
            device_name=entry.get("device_name", profile),
            platform_name=entry.get("platform", self._settings.platform),
            udid=entry.get("udid"),
            platform_version=entry.get("platform_version"),
            automation_name=entry.get("automation_name"),
            is_simulator=entry.get("is_simulator", False),
        )

    # ------------------------------------------------------------------
    # Tier 3 - auto-detect
    # ------------------------------------------------------------------

    def _auto_detect(self) -> DeviceInfo | None:
        if self._settings.platform == "android":
            return self._detect_android()
        if self._settings.platform == "ios":
            return self._detect_ios()
        return None

    # Android auto-detect via adb

    def _detect_android(self) -> DeviceInfo | None:
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

        connected = [
            line.split()[0]
            for line in result.stdout.strip().splitlines()[1:]
            if len(line.split()) >= 2 and line.split()[1] == "device"
        ]

        if not connected:
            return None

        if len(connected) > 1:
            warnings.warn(
                f"Multiple Android devices detected ({connected}). "
                "The first device will be used. Set APP_UDID to target a specific device.",
                stacklevel=2,
            )

        udid = connected[0]
        version = self._adb_getprop(udid, "ro.build.version.release")
        model = self._adb_getprop(udid, "ro.product.model") or udid
        return DeviceInfo(
            device_name=model,
            platform_name="android",
            udid=udid,
            platform_version=version,
            is_simulator=False,
        )

    def _adb_getprop(self, udid: str, prop: str) -> str | None:
        try:
            result = subprocess.run(
                ["adb", "-s", udid, "shell", "getprop", prop],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip() or None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

    # iOS auto-detect via xcrun

    def _detect_ios(self) -> DeviceInfo | None:
        detected = self._detect_ios_simulator()
        if detected:
            return detected
        return self._detect_ios_device()

    def _detect_ios_simulator(self) -> DeviceInfo | None:
        try:
            result = subprocess.run(
                ["xcrun", "simctl", "list", "devices", "--json"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            data: dict[str, Any] = json.loads(result.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            return None

        for runtime, devices in data.get("devices", {}).items():
            for device in devices:
                if device.get("state") == "Booted":
                    # runtime looks like "com.apple.CoreSimulator.SimRuntime.iOS-17-4"
                    parts = runtime.rsplit("-", 2)
                    version = f"{parts[-2]}.{parts[-1]}" if len(parts) >= 3 else None
                    return DeviceInfo(
                        device_name=device["name"],
                        platform_name="ios",
                        udid=device.get("udid"),
                        platform_version=version,
                        is_simulator=True,
                    )
        return None

    def _detect_ios_device(self) -> DeviceInfo | None:
        try:
            result = subprocess.run(
                ["xcrun", "xctrace", "list", "devices"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or "Simulator" in line or line.startswith("=="):
                continue
            # Lines look like: "iPhone 15 Pro (17.4) (UDID)"
            parts = line.rsplit("(", 2)
            if len(parts) < 3:
                continue
            name = parts[0].strip()
            lowered_name = name.lower()
            if (
                lowered_name in {"mac", "my mac"}
                or "macbook" in lowered_name
                or "imac" in lowered_name
            ):
                continue

            version = parts[1].rstrip(")").strip() or None
            udid_part = parts[-1].rstrip(")").strip()
            if not _IOS_UDID_RE.fullmatch(udid_part):
                continue

            return DeviceInfo(
                device_name=name,
                platform_name="ios",
                udid=udid_part,
                platform_version=version,
                is_simulator=False,
            )
        return None


def validate_launch_config(settings: "AppiumPytestKitSettings") -> None:
    """Raise LaunchValidationError when required app launch settings are missing."""
    from appium_pytest_kit.driver import discover_latest_app_build
    from appium_pytest_kit.errors import LaunchValidationError

    resolved_app = settings.app or discover_latest_app_build(settings)

    if settings.platform == "android":
        has_app = bool(resolved_app)
        has_activity = bool(settings.app_package and settings.app_activity)
        if not has_app and not has_activity:
            msg = (
                "Android launch requires APP_APP (apk path) "
                "or both APP_APP_PACKAGE + APP_APP_ACTIVITY. "
                "If APP_APP_AUTO_DISCOVER=true, ensure a build exists under APP_APP_BUILDS_DIR."
            )
            raise LaunchValidationError(msg)

    elif settings.platform == "ios":
        has_app = bool(resolved_app)
        has_bundle = bool(settings.bundle_id)
        if not has_app and not has_bundle:
            msg = (
                "iOS launch requires APP_APP (ipa/app path) or APP_BUNDLE_ID. "
                "If APP_APP_AUTO_DISCOVER=true, ensure a build exists under APP_APP_BUILDS_DIR."
            )
            raise LaunchValidationError(msg)
