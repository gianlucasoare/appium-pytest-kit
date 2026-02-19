"""Configuration loading and merge rules for appium-pytest-kit."""


import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    new_command_timeout: int = 120
    no_reset: bool = False
    full_reset: bool = False
    implicit_wait: float = 0.0

    capabilities_json: dict[str, Any] = Field(default_factory=dict)

    reporting_enabled: bool = False
    report_dir: Path = Path("artifacts/appium-pytest-kit")

    @field_validator("platform")
    @classmethod
    def _validate_platform(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"android", "ios"}:
            msg = "platform must be 'android' or 'ios'"
            raise ValueError(msg)
        return normalized

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


def load_settings(*, env_file: str | Path | None = None) -> AppiumPytestKitSettings:
    """Load framework settings from defaults + .env + env vars."""

    if env_file is None:
        return AppiumPytestKitSettings()
    return AppiumPytestKitSettings(_env_file=env_file)


def _normalize_setting_name(name: str) -> str:
    normalized = name.strip().lower().replace("-", "_")
    if normalized.startswith("app_"):
        normalized = normalized.removeprefix("app_")
    return normalized


def apply_cli_overrides(
    settings: AppiumPytestKitSettings,
    overrides: Mapping[str, Any],
) -> AppiumPytestKitSettings:
    """Apply highest-precedence CLI overrides on top of loaded settings."""

    merged = settings.model_dump(mode="python")
    for raw_key, raw_value in overrides.items():
        if raw_value is None:
            continue
        merged[_normalize_setting_name(raw_key)] = raw_value
    return AppiumPytestKitSettings.model_validate(merged)
