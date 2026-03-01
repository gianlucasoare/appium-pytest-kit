"""Configuration loading and merge rules for appium-pytest-kit."""


import json
import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_KNOWN_CAPABILITY_KEYS: set[str] = {
    # W3C / core
    "platformName",
    "browserName",
    "browserVersion",
    "acceptInsecureCerts",
    "pageLoadStrategy",
    "proxy",
    "setWindowRect",
    "timeouts",
    "unhandledPromptBehavior",
    "automationName",
    "newCommandTimeout",
    "deviceName",
    "platformVersion",
    "udid",
    "app",
    "noReset",
    "fullReset",
    # Android
    "appPackage",
    "appActivity",
    "appWaitActivity",
    "appWaitPackage",
    "appWaitDuration",
    "autoGrantPermissions",
    "adbExecTimeout",
    "systemPort",
    "chromedriverExecutable",
    "chromedriverArgs",
    "unicodeKeyboard",
    "resetKeyboard",
    "autoWebview",
    "autoWebviewTimeout",
    # iOS
    "bundleId",
    "autoAcceptAlerts",
    "wdaLocalPort",
    "showXcodeLog",
    "useNewWDA",
    "wdaStartupRetries",
    "wdaStartupRetryInterval",
    "webkitDebugProxyPort",
    "xcodeOrgId",
    "xcodeSigningId",
    "updatedWDABundleId",
    "connectHardwareKeyboard",
    "simpleIsVisibleCheck",
    "forceAppLaunch",
    "shouldTerminateApp",
    # Common extra caps
    "language",
    "locale",
}


def _is_known_capability_key(key: str) -> bool:
    normalized = key.strip()
    if not normalized:
        return False
    # Namespaced extension capabilities are valid by definition.
    if ":" in normalized:
        return True
    return normalized in _KNOWN_CAPABILITY_KEYS


def _unknown_capability_keys(capabilities: Mapping[str, Any]) -> list[str]:
    unknown = [str(key) for key in capabilities.keys() if not _is_known_capability_key(str(key))]
    return sorted(set(unknown))


def validate_capabilities_for_strict(capabilities: Mapping[str, Any], *, strict: bool) -> None:
    """Validate capability key names when strict config mode is enabled."""

    if not strict:
        return
    unknown = _unknown_capability_keys(capabilities)
    if not unknown:
        return
    rendered = ", ".join(repr(key) for key in unknown)
    msg = (
        "Strict config rejected unknown capability key(s): "
        f"{rendered}. Use standard Appium names or vendor-prefixed keys (e.g. 'appium:foo')."
    )
    raise ValueError(msg)


def _normalize_capability_key(raw_key: str) -> str:
    key = raw_key.strip()
    # Allow env-style capability names in --app-override:
    # APP_AUTO_GRANT_PERMISSIONS -> autoGrantPermissions
    if key.upper().startswith("APP_"):
        tail = key[4:]
        parts = [part for part in tail.lower().split("_") if part]
        if parts:
            return parts[0] + "".join(part.title() for part in parts[1:])
    return key


def _coerce_capability_value(raw: Any) -> Any:
    if not isinstance(raw, str):
        return raw
    payload = raw.strip()
    if payload == "":
        return raw
    try:
        return json.loads(payload)
    except ValueError:
        lowered = payload.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        if lowered in {"null", "none"}:
            return None
        return raw


_ENV_ASSIGNMENT_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")


def _known_setting_env_keys() -> set[str]:
    return {f"APP_{field_name.upper()}" for field_name in AppiumPytestKitSettings.model_fields}


def _read_env_keys_from_file(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        payload = path.read_text(encoding="utf-8")
    except OSError:
        return set()

    keys: set[str] = set()
    for line in payload.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _ENV_ASSIGNMENT_RE.match(line)
        if match:
            keys.add(match.group(1).upper())
    return keys


def _unknown_setting_env_keys(*, env_file: Path | None) -> list[str]:
    known = {key.upper() for key in _known_setting_env_keys()}

    observed: set[str] = set()
    observed.update(
        key.upper()
        for key in os.environ
        if key.upper().startswith("APP_")
    )
    if env_file is not None:
        observed.update(_read_env_keys_from_file(env_file))

    unknown = sorted(key for key in observed if key not in known)
    return unknown


class AppiumPytestKitSettings(BaseSettings):
    """Framework settings loaded from defaults and environment."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    platform: str = "android"
    appium_url: str = "http://127.0.0.1:4723"

    manage_appium_server: bool = False
    appium_host: str = "127.0.0.1"
    appium_port: int = 4723
    appium_base_path: str = "/"
    appium_server_args: tuple[str, ...] = ()
    appium_start_timeout: float = 20.0

    device_name: str | None = None
    platform_version: str | None = None
    udid: str | None = None

    app: str | None = None
    app_package: str | None = None
    app_activity: str | None = None
    bundle_id: str | None = None
    automation_name: str | None = None
    app_auto_discover: bool = False
    app_builds_dir: Path = Path("app_builds")

    new_command_timeout: int = 120
    no_reset: bool = False
    full_reset: bool = False
    implicit_wait: float = 0.0

    capabilities_json: dict[str, Any] = Field(default_factory=dict)

    session_mode: Literal["clean", "clean-session", "debug"] = "clean"
    """Driver session lifecycle strategy.

    - ``clean``         — a fresh Appium session is created and quit for every test function
                          (default; maximum isolation, slower due to session startup overhead).
    - ``clean-session`` — a single Appium session is shared across the whole test suite and
                          quit once at the end (faster, but tests share driver state).
    - ``debug``         — same as ``clean-session``; failures do not restart the session,
                          and it is still quit automatically at session end.
    """

    explicit_wait_timeout: float = 10.0
    """Default timeout in seconds used by ``Waiter`` and ``MobileActions`` explicit waits.

    This is independent of ``implicit_wait`` (the Appium-level driver implicit wait).
    Set via ``APP_EXPLICIT_WAIT_TIMEOUT``.
    """

    device_profile: str | None = None
    devices_yaml: Path = Path("data/devices.yaml")
    is_simulator: bool = False
    video_policy: Literal["always", "failed", "never"] = "never"
    artifacts_dir: Path = Path("artifacts")
    clean_artifacts_on_start: bool = False
    artifact_redaction_enabled: bool = False
    artifact_redact_screenshots: bool = False
    artifact_redaction_replacement: str = "[REDACTED]"
    artifact_redaction_patterns: tuple[str, ...] = ()
    appium_preflight_status: bool = True
    strict_config: bool = False

    reporting_enabled: bool = False
    report_dir: Path = Path("artifacts/appium-pytest-kit")
    quarantine_mode: Literal["run", "skip"] = "run"
    perf_enabled: bool = False
    perf_budget_action_ms: float | None = None
    perf_budget_test_ms: float | None = None
    perf_budget_session_start_ms: float | None = None
    perf_trend_history_limit: int = 30

    @field_validator("platform")
    @classmethod
    def _validate_platform(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"android", "ios"}:
            msg = "platform must be 'android' or 'ios'"
            raise ValueError(msg)
        return normalized

    @field_validator(
        "device_name",
        "platform_version",
        "udid",
        "app",
        "app_package",
        "app_activity",
        "bundle_id",
        "automation_name",
        "device_profile",
        mode="before",
    )
    @classmethod
    def _normalize_blank_optional_strings(cls, value: Any) -> Any:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator("appium_base_path")
    @classmethod
    def _normalize_base_path(cls, value: str) -> str:
        cleaned = value.strip() or "/"
        return cleaned if cleaned.startswith("/") else f"/{cleaned}"

    @field_validator("appium_server_args", mode="before")
    @classmethod
    def _parse_server_args(cls, value: Any) -> tuple[str, ...]:
        if value is None or value == "":
            return ()
        if isinstance(value, str):
            return tuple(part.strip() for part in value.split(",") if part.strip())
        if isinstance(value, (list, tuple)):
            return tuple(str(item).strip() for item in value if str(item).strip())
        msg = "appium_server_args must be a comma-separated string or a sequence"
        raise TypeError(msg)

    @field_validator("capabilities_json", mode="before")
    @classmethod
    def _parse_capabilities_json(cls, value: Any) -> dict[str, Any]:
        if value is None or value == "":
            return {}
        if isinstance(value, str):
            loaded = json.loads(value)
            if not isinstance(loaded, dict):
                msg = "capabilities_json JSON payload must decode to an object"
                raise ValueError(msg)
            return loaded
        if isinstance(value, Mapping):
            return dict(value)
        msg = "capabilities_json must be a JSON object string or mapping"
        raise TypeError(msg)

    @field_validator("artifact_redaction_patterns", mode="before")
    @classmethod
    def _parse_artifact_redaction_patterns(cls, value: Any) -> tuple[str, ...]:
        if value is None or value == "":
            return ()
        if isinstance(value, str):
            return tuple(part.strip() for part in value.split(",") if part.strip())
        if isinstance(value, (list, tuple)):
            return tuple(str(item).strip() for item in value if str(item).strip())
        msg = "artifact_redaction_patterns must be a comma-separated string or a sequence"
        raise TypeError(msg)

    @field_validator(
        "perf_budget_action_ms",
        "perf_budget_test_ms",
        "perf_budget_session_start_ms",
    )
    @classmethod
    def _validate_optional_positive_ms(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if value <= 0:
            msg = "performance budget values must be > 0 milliseconds"
            raise ValueError(msg)
        return value

    @field_validator("perf_trend_history_limit")
    @classmethod
    def _validate_perf_trend_history_limit(cls, value: int) -> int:
        if value < 1:
            msg = "perf_trend_history_limit must be >= 1"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def _validate_strict_capabilities(self) -> "AppiumPytestKitSettings":
        validate_capabilities_for_strict(self.capabilities_json, strict=self.strict_config)
        return self


def load_settings(*, env_file: str | Path | None = None) -> AppiumPytestKitSettings:
    """Load framework settings from defaults + .env + env vars."""

    env_path = Path(".env") if env_file is None else Path(env_file)
    if env_file is None:
        settings = AppiumPytestKitSettings()
    else:
        settings = AppiumPytestKitSettings(_env_file=env_file)

    if settings.strict_config:
        unknown_env_keys = _unknown_setting_env_keys(env_file=env_path)
        if unknown_env_keys:
            rendered = ", ".join(repr(key) for key in unknown_env_keys)
            msg = (
                "Strict config rejected unknown APP_* setting key(s): "
                f"{rendered}. Use declared APP_ setting names or APP_CAPABILITIES_JSON."
            )
            raise ValueError(msg)

    return settings


def _normalize_setting_name(name: str) -> str:
    normalized = name.strip().replace("-", "_")
    if normalized.lower().startswith("app_"):
        normalized = normalized[4:]
    # Accept camelCase/PascalCase (e.g. noReset) as well as snake_case.
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    return normalized.lower()


def apply_cli_overrides(
    settings: AppiumPytestKitSettings,
    overrides: Mapping[str, Any],
) -> AppiumPytestKitSettings:
    """Apply highest-precedence CLI overrides on top of loaded settings."""

    merged = settings.model_dump(mode="python")
    known_fields = set(AppiumPytestKitSettings.model_fields.keys())
    pending_capability_overrides: list[tuple[str, Any]] = []

    for raw_key, raw_value in overrides.items():
        if raw_value is None:
            continue
        key = _normalize_setting_name(raw_key)
        if key not in known_fields:
            pending_capability_overrides.append((raw_key, raw_value))
            continue
        merged[key] = raw_value

    # Resolve strict mode after setting overrides have been applied, so
    # APP_STRICT_CONFIG can be toggled from the same CLI invocation.
    strict_mode = bool(AppiumPytestKitSettings.model_validate(merged).strict_config)
    capability_overrides = dict(merged.get("capabilities_json") or {})
    unknown_capability_keys: list[str] = []

    for raw_key, raw_value in pending_capability_overrides:
        capability_key = _normalize_capability_key(raw_key)
        if strict_mode and not _is_known_capability_key(capability_key):
            unknown_capability_keys.append(raw_key)
            continue
        capability_overrides[capability_key] = _coerce_capability_value(raw_value)

    if unknown_capability_keys:
        rendered = ", ".join(repr(key) for key in unknown_capability_keys)
        msg = (
            "Unknown appium-pytest-kit override(s) in strict mode: "
            f"{rendered}. Use declared setting names or valid capability keys."
        )
        raise ValueError(msg)

    merged["capabilities_json"] = capability_overrides

    return AppiumPytestKitSettings.model_validate(merged)
