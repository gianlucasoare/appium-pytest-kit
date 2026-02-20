
from pathlib import Path

import pytest

from appium_pytest_kit.settings import AppiumPytestKitSettings, apply_cli_overrides, load_settings


def test_load_settings_from_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "APP_PLATFORM=ios",
                "APP_APPIUM_URL=http://127.0.0.1:4999",
                'APP_CAPABILITIES_JSON={"language":"en"}',
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file=env_file)

    assert settings.platform == "ios"
    assert settings.appium_url == "http://127.0.0.1:4999"
    assert settings.capabilities_json == {"language": "en"}


def test_cli_overrides_are_highest_precedence(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("APP_PLATFORM=ios\n", encoding="utf-8")

    base = load_settings(env_file=env_file)
    merged = apply_cli_overrides(
        base,
        {
            "APP_PLATFORM": "android",
            "appium_url": "http://127.0.0.1:4725",
        },
    )

    assert base.platform == "ios"
    assert merged.platform == "android"
    assert merged.appium_url == "http://127.0.0.1:4725"


def test_cli_overrides_accept_camel_case_keys() -> None:
    base = AppiumPytestKitSettings()
    merged = apply_cli_overrides(base, {"noReset": "true"})
    assert merged.no_reset is True


def test_cli_overrides_unknown_keys_become_capabilities_in_default_mode() -> None:
    base = AppiumPytestKitSettings()
    merged = apply_cli_overrides(base, {"autoGrantPermissions": "true"})
    assert merged.capabilities_json["autoGrantPermissions"] is True


def test_cli_overrides_reject_unknown_keys_in_strict_mode() -> None:
    base = AppiumPytestKitSettings(strict_config=True)
    with pytest.raises(ValueError, match="unknownField"):
        apply_cli_overrides(base, {"unknownField": "x"})


def test_strict_mode_rejects_unknown_capabilities_json_key() -> None:
    with pytest.raises(ValueError, match="unknown capability key"):
        AppiumPytestKitSettings(strict_config=True, capabilities_json={"totallyUnknownCap": True})


def test_strict_mode_allows_namespaced_capabilities() -> None:
    settings = AppiumPytestKitSettings(
        strict_config=True,
        capabilities_json={"appium:customCap": "x"},
    )
    assert settings.capabilities_json["appium:customCap"] == "x"


def test_blank_optional_env_values_are_normalized_to_none(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "APP_PLATFORM=android",
                "APP_APP=",
                "APP_APP_PACKAGE=",
                "APP_APP_ACTIVITY=",
                "APP_DEVICE_NAME=",
                "APP_UDID=",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file=env_file)
    assert settings.app is None
    assert settings.app_package is None
    assert settings.app_activity is None
    assert settings.device_name is None
    assert settings.udid is None


def test_strict_mode_allows_w3c_browser_name() -> None:
    settings = AppiumPytestKitSettings(
        strict_config=True,
        capabilities_json={"browserName": "Chrome"},
    )
    assert settings.capabilities_json["browserName"] == "Chrome"
