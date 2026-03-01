"""Failure artifact capture helpers (screenshot + page source)."""


import base64
import re
import subprocess
import warnings
from pathlib import Path
from typing import Any

_TRANSPARENT_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/xFoAAAAASUVORK5CYII="
)
_DEFAULT_REDACTION_PATTERNS: tuple[str, ...] = (
    r"(?i)(authorization\s*:\s*bearer\s+)([A-Za-z0-9\-._~+/]+=*)",
    r"(?i)(access[_-]?token[\s\"'=:\[]+)([A-Za-z0-9\-._~+/]+=*)",
    r"(?i)(refresh[_-]?token[\s\"'=:\[]+)([A-Za-z0-9\-._~+/]+=*)",
    r"(?i)(api[_-]?key[\s\"'=:\[]+)([A-Za-z0-9\-._~+/]+=*)",
    r"(?i)(password[\s\"'=:\[]+)([^\\s\"']+)",
)


def _safe_filename(node_id: str) -> str:
    """Convert a pytest node ID to a safe filesystem stem."""
    return re.sub(r"[^\w\-]", "_", node_id.replace("::", "__").replace("/", "_"))


def _redact_text(
    payload: str,
    *,
    enabled: bool,
    replacement: str = "[REDACTED]",
    extra_patterns: tuple[str, ...] = (),
) -> str:
    if not enabled:
        return payload

    redacted = payload
    for pattern in (*_DEFAULT_REDACTION_PATTERNS, *tuple(extra_patterns)):
        try:
            compiled = re.compile(pattern)
        except re.error:
            continue

        def _replace(match: re.Match[str]) -> str:
            if match.lastindex and match.lastindex >= 2:
                return f"{match.group(1)}{replacement}"
            return replacement

        redacted = compiled.sub(_replace, redacted)
    return redacted


def capture_screenshot(
    driver,
    node_id: str,
    artifacts_dir: Path,
    *,
    redact: bool = False,
    redact_screenshot: bool = False,
) -> Path | None:
    """Save a PNG screenshot and return the path, or None on failure."""

    try:
        dest = artifacts_dir / "screenshots" / f"{_safe_filename(node_id)}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if redact and redact_screenshot:
            dest.write_bytes(_TRANSPARENT_PIXEL_PNG)
            return dest
        driver.save_screenshot(str(dest))
        return dest
    except Exception as exc:
        warnings.warn(
            f"Failed to capture screenshot for {node_id!r}: {exc}",
            stacklevel=2,
        )
        return None


def capture_page_source(
    driver,
    node_id: str,
    artifacts_dir: Path,
    *,
    redact: bool = False,
    redaction_patterns: tuple[str, ...] = (),
    redaction_replacement: str = "[REDACTED]",
) -> Path | None:
    """Save page source XML and return the path, or None on failure."""

    try:
        dest = artifacts_dir / "pagesource" / f"{_safe_filename(node_id)}.xml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        source = str(driver.page_source)
        source = _redact_text(
            source,
            enabled=redact,
            replacement=redaction_replacement,
            extra_patterns=tuple(redaction_patterns),
        )
        dest.write_text(source, encoding="utf-8")
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
    redact: bool = False,
    redaction_patterns: tuple[str, ...] = (),
    redaction_replacement: str = "[REDACTED]",
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

        payload = _redact_text(
            payload,
            enabled=redact,
            replacement=redaction_replacement,
            extra_patterns=tuple(redaction_patterns),
        )
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


def _render_driver_log_payload(log_type: str, entries: Any) -> str | None:
    if entries is None:
        return None
    if not isinstance(entries, list):
        return str(entries) if str(entries).strip() else None

    lines: list[str] = [f"# appium-log-type: {log_type}"]
    for entry in entries:
        if isinstance(entry, dict):
            timestamp = entry.get("timestamp", "")
            level = entry.get("level", "")
            message = entry.get("message", "")
            rendered = f"[{timestamp}] {level} {message}".strip()
            lines.append(rendered)
        else:
            lines.append(str(entry))
    payload = "\n".join(lines).strip()
    return payload or None


def capture_session_log(
    driver: Any,
    node_id: str,
    artifacts_dir: Path,
    *,
    redact: bool = False,
    redaction_patterns: tuple[str, ...] = (),
    redaction_replacement: str = "[REDACTED]",
) -> Path | None:
    """Capture Appium session logs via ``driver.get_log`` and return saved path."""

    preferred_types = ("server", "logcat", "syslog", "crashlog", "browser")

    try:
        available_types = getattr(driver, "log_types", None)
        if available_types is None:
            candidates = list(preferred_types)
        elif isinstance(available_types, (list, tuple, set)):
            normalized = [str(item) for item in available_types]
            prioritized = [kind for kind in preferred_types if kind in normalized]
            candidates = prioritized or normalized
        else:
            candidates = list(preferred_types)

        for log_type in candidates:
            try:
                entries = driver.get_log(log_type)
            except Exception:
                continue
            payload = _render_driver_log_payload(log_type, entries)
            if not payload:
                continue

            payload = _redact_text(
                payload,
                enabled=redact,
                replacement=redaction_replacement,
                extra_patterns=tuple(redaction_patterns),
            )
            dest = artifacts_dir / "session_logs" / f"{_safe_filename(node_id)}.log"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(payload, encoding="utf-8")
            return dest
        return None
    except Exception as exc:
        warnings.warn(
            f"Failed to capture session logs for {node_id!r}: {exc}",
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
