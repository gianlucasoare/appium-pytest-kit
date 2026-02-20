"""Failure artifact capture helpers (screenshot + page source)."""


import re
import subprocess
import warnings
from pathlib import Path
from typing import Any


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


def _driver_capability(driver, key: str) -> str | None:
    capabilities = getattr(driver, "capabilities", None)
    if not isinstance(capabilities, dict):
        return None
    value = capabilities.get(key)
    if value is None:
        return None
    rendered = str(value).strip()
    return rendered or None


def _run_capture_command(command: list[str], *, timeout: float = 8.0) -> str | None:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, PermissionError):
        return None
    except subprocess.TimeoutExpired as exc:
        partial = (exc.stdout or "") + ("\n" + exc.stderr if exc.stderr else "")
        payload = partial.strip()
        return payload or None

    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    payload = output.strip()
    return payload or None


def _capture_android_logs(udid: str | None) -> str | None:
    base = ["adb"]
    if udid:
        base.extend(["-s", udid])
    # `-d` dumps and exits; `-v time` includes timestamps for triage.
    command = [*base, "logcat", "-d", "-v", "time"]
    return _run_capture_command(command, timeout=10.0)


def _capture_ios_logs(udid: str | None, is_simulator: bool) -> str | None:
    if is_simulator:
        targets: list[str] = []
        if udid:
            targets.append(udid)
        targets.append("booted")
        for target in dict.fromkeys(targets):
            payload = _run_capture_command(
                [
                    "xcrun",
                    "simctl",
                    "spawn",
                    target,
                    "log",
                    "show",
                    "--style",
                    "compact",
                    "--last",
                    "15m",
                ],
                timeout=10.0,
            )
            if payload:
                return payload
        return None

    if udid:
        payload = _run_capture_command(
            ["xcrun", "devicectl", "device", "log", "show", "--device", udid],
            timeout=8.0,
        )
        if payload:
            return payload
        return _run_capture_command(["idevicesyslog", "-u", udid], timeout=3.0)

    return _run_capture_command(["idevicesyslog"], timeout=3.0)


def capture_device_logs(
    driver: Any,
    node_id: str,
    artifacts_dir: Path,
    *,
    platform: str | None = None,
    udid: str | None = None,
    is_simulator: bool = False,
) -> Path | None:
    """Capture platform logs (adb / iOS) and return saved path, or None."""

    try:
        effective_platform = (platform or _driver_capability(driver, "platformName") or "").lower()
        effective_udid = udid or _driver_capability(driver, "udid")

        if effective_platform == "android":
            payload = _capture_android_logs(effective_udid)
        elif effective_platform == "ios":
            payload = _capture_ios_logs(effective_udid, is_simulator)
        else:
            return None

        if not payload:
            return None

        dest = artifacts_dir / "device_logs" / f"{_safe_filename(node_id)}.log"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(payload, encoding="utf-8")
        return dest
    except Exception as exc:
        warnings.warn(
            f"Failed to capture device logs for {node_id!r}: {exc}",
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
