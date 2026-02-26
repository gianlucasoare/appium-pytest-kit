"""Tests for the appium-pytest-kit doctor CLI."""

import json
import subprocess
from pathlib import Path
from urllib.error import URLError

from appium_pytest_kit.cli import doctor_main
from appium_pytest_kit.settings import AppiumPytestKitSettings


def _android_settings(tmp_path: Path) -> AppiumPytestKitSettings:
    return AppiumPytestKitSettings(
        platform="android",
        appium_url="http://127.0.0.1:4723",
        app_package="com.example",
        app_activity=".MainActivity",
        artifacts_dir=tmp_path / "artifacts",
    )


def _ios_settings(tmp_path: Path) -> AppiumPytestKitSettings:
    return AppiumPytestKitSettings(
        platform="ios",
        appium_url="http://127.0.0.1:4723",
        bundle_id="com.example.ios",
        artifacts_dir=tmp_path / "artifacts",
    )


def test_doctor_main_passes_android_checks(monkeypatch, tmp_path: Path, capsys) -> None:
    settings = _android_settings(tmp_path)
    monkeypatch.setattr("appium_pytest_kit.cli.load_settings", lambda env_file=None: settings)

    def _run_command(command, *, timeout=8.0):
        _ = timeout
        if list(command[:2]) == ["appium", "--version"]:
            return subprocess.CompletedProcess(command, 0, stdout="2.5.4\n", stderr="")
        if list(command[:4]) == ["appium", "driver", "list", "--installed"]:
            payload = '{"installed":[{"name":"uiautomator2","version":"3.1.0"}]}'
            return subprocess.CompletedProcess(command, 0, stdout=payload, stderr="")
        if list(command[:2]) == ["adb", "version"]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="Android Debug Bridge version 1.0.41\n",
                stderr="",
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr("appium_pytest_kit.cli._run_command", _run_command)
    code = doctor_main(["--no-server-check"])
    output = capsys.readouterr().out

    assert code == 0
    assert "[PASS] appium cli" in output
    assert "[PASS] adb" in output
    assert "[PASS] appium drivers" in output
    assert "[WARN] appium server: server check skipped by --no-server-check" in output


def test_doctor_main_fails_when_ios_tool_missing(monkeypatch, tmp_path: Path, capsys) -> None:
    settings = _ios_settings(tmp_path)
    monkeypatch.setattr("appium_pytest_kit.cli.load_settings", lambda env_file=None: settings)

    def _run_command(command, *, timeout=8.0):
        _ = timeout
        if list(command[:2]) == ["appium", "--version"]:
            return subprocess.CompletedProcess(command, 0, stdout="2.5.4\n", stderr="")
        if list(command[:4]) == ["appium", "driver", "list", "--installed"]:
            payload = '{"installed":[{"name":"xcuitest","version":"7.0.0"}]}'
            return subprocess.CompletedProcess(command, 0, stdout=payload, stderr="")
        if list(command[:2]) == ["xcrun", "--version"]:
            raise FileNotFoundError
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr("appium_pytest_kit.cli._run_command", _run_command)
    code = doctor_main(["--no-server-check"])
    output = capsys.readouterr().out

    assert code == 1
    assert "[FAIL] xcrun" in output


def test_doctor_main_fails_on_unreachable_server(monkeypatch, tmp_path: Path, capsys) -> None:
    settings = _android_settings(tmp_path)
    monkeypatch.setattr("appium_pytest_kit.cli.load_settings", lambda env_file=None: settings)

    def _run_command(command, *, timeout=8.0):
        _ = timeout
        if list(command[:2]) == ["appium", "--version"]:
            return subprocess.CompletedProcess(command, 0, stdout="2.5.4\n", stderr="")
        if list(command[:4]) == ["appium", "driver", "list", "--installed"]:
            payload = '{"installed":[{"name":"uiautomator2","version":"3.1.0"}]}'
            return subprocess.CompletedProcess(command, 0, stdout=payload, stderr="")
        if list(command[:2]) == ["adb", "version"]:
            return subprocess.CompletedProcess(command, 0, stdout="Android Debug Bridge", stderr="")
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr("appium_pytest_kit.cli._run_command", _run_command)
    monkeypatch.setattr(
        "appium_pytest_kit.cli.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(URLError("offline")),
    )

    code = doctor_main([])
    output = capsys.readouterr().out
    assert code == 1
    assert "[FAIL] appium server" in output


def test_doctor_main_json_output(monkeypatch, tmp_path: Path, capsys) -> None:
    settings = _android_settings(tmp_path)
    monkeypatch.setattr("appium_pytest_kit.cli.load_settings", lambda env_file=None: settings)

    def _run_command(command, *, timeout=8.0):
        _ = timeout
        if list(command[:2]) == ["appium", "--version"]:
            return subprocess.CompletedProcess(command, 0, stdout="2.5.4\n", stderr="")
        if list(command[:4]) == ["appium", "driver", "list", "--installed"]:
            payload = '{"installed":[{"name":"uiautomator2","version":"3.1.0"}]}'
            return subprocess.CompletedProcess(command, 0, stdout=payload, stderr="")
        if list(command[:2]) == ["adb", "version"]:
            return subprocess.CompletedProcess(command, 0, stdout="Android Debug Bridge", stderr="")
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr("appium_pytest_kit.cli._run_command", _run_command)
    code = doctor_main(["--no-server-check", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["ok"] is True
    assert payload["summary"]["failed"] == 0
    assert any(check["name"] == "appium cli" for check in payload["checks"])
