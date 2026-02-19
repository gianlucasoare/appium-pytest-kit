"""Tests for Phase 2 settings fields."""

from pathlib import Path

import pytest

from appium_pytest_kit.settings import AppiumPytestKitSettings, load_settings


def test_session_mode_default() -> None:
    s = AppiumPytestKitSettings()
    assert s.session_mode == "clean"


def test_session_mode_values(tmp_path: Path) -> None:
    for mode in ("clean", "clean-session", "debug"):
        env = tmp_path / f".env_{mode}"
        env.write_text(f"APP_SESSION_MODE={mode}\n", encoding="utf-8")
        s = load_settings(env_file=env)
        assert s.session_mode == mode


def test_invalid_session_mode_raises(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("APP_SESSION_MODE=turbo\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_settings(env_file=env)


def test_video_policy_default() -> None:
    s = AppiumPytestKitSettings()
    assert s.video_policy == "never"


def test_video_policy_values(tmp_path: Path) -> None:
    for policy in ("always", "failed", "never"):
        env = tmp_path / f".env_{policy}"
        env.write_text(f"APP_VIDEO_POLICY={policy}\n", encoding="utf-8")
        s = load_settings(env_file=env)
        assert s.video_policy == policy


def test_artifacts_dir_default() -> None:
    s = AppiumPytestKitSettings()
    assert s.artifacts_dir == Path("artifacts")


def test_artifacts_dir_from_env(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("APP_ARTIFACTS_DIR=/tmp/my-artifacts\n", encoding="utf-8")
    s = load_settings(env_file=env)
    assert s.artifacts_dir == Path("/tmp/my-artifacts")


def test_devices_yaml_default() -> None:
    s = AppiumPytestKitSettings()
    assert s.devices_yaml == Path("data/devices.yaml")


def test_is_simulator_default() -> None:
    s = AppiumPytestKitSettings()
    assert s.is_simulator is False


def test_device_profile_default() -> None:
    s = AppiumPytestKitSettings()
    assert s.device_profile is None
