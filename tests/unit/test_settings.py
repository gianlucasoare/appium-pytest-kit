
from pathlib import Path

from appium_pytest_kit.settings import apply_cli_overrides, load_settings


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
