
from pathlib import Path

from appium_pytest_kit.cli import ENV_TEMPLATE, init_env_file, main


def test_init_env_file_creates_template(tmp_path: Path) -> None:
    target = tmp_path / ".env"

    created = init_env_file(target)

    assert created is True
    assert target.read_text(encoding="utf-8") == ENV_TEMPLATE


def test_init_env_file_respects_force_flag(tmp_path: Path) -> None:
    target = tmp_path / ".env"
    target.write_text("APP_PLATFORM=ios\n", encoding="utf-8")

    skipped = init_env_file(target, force=False)
    overwritten = init_env_file(target, force=True)

    assert skipped is False
    assert overwritten is True
    assert "APP_PLATFORM=android" in target.read_text(encoding="utf-8")


def test_main_returns_zero_when_target_exists(capsys, tmp_path: Path) -> None:
    target = tmp_path / ".env"
    target.write_text("APP_PLATFORM=ios\n", encoding="utf-8")

    code = main(["--path", str(target)])

    captured = capsys.readouterr()
    assert code == 0
    assert "Skipped" in captured.out
