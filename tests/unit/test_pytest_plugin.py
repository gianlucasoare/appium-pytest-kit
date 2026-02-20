"""Targeted tests for pytest plugin lifecycle and option wiring."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from appium_pytest_kit import pytest_plugin
from appium_pytest_kit._internal.device_resolver import DeviceInfo
from appium_pytest_kit.errors import ConfigurationError


class _FakeGroup:
    def __init__(self) -> None:
        self.calls: list[tuple[tuple[str, ...], dict]] = []

    def addoption(self, *args: str, **kwargs) -> None:
        self.calls.append((args, kwargs))


class _FakeParser:
    def __init__(self) -> None:
        self.group = _FakeGroup()

    def getgroup(self, _name: str) -> _FakeGroup:
        return self.group


class _FakeNode:
    def __init__(self, nodeid: str) -> None:
        self.nodeid = nodeid
        self.stash: dict = {}


class _FakeRequest:
    def __init__(self, config, node: _FakeNode) -> None:
        self.config = config
        self.node = node


class _FakeConfig:
    def __init__(self) -> None:
        self.stash: dict = {
            pytest_plugin.RETRY_DRIVER_REGISTRY_KEY: {},
            pytest_plugin.RETRY_RECORDER_REGISTRY_KEY: {},
        }
        self.pluginmanager = SimpleNamespace(
            hook=SimpleNamespace(
                pytest_appium_pytest_kit_driver_created=MagicMock(),
                pytest_appium_pytest_kit_configure_settings=MagicMock(return_value=None),
            )
        )

    def getoption(self, name: str, default=None):
        if name == "app_override":
            return ["unknownField=1"]
        return default


def test_pytest_addoption_registers_appium_url_alias() -> None:
    parser = _FakeParser()
    pytest_plugin.pytest_addoption(parser)  # type: ignore[arg-type]
    assert any(
        "--app-appium-url" in args and "--appium-url" in args for args, _ in parser.group.calls
    )


def test_driver_retry_reuses_session_and_preserves_recorder(monkeypatch) -> None:
    settings = SimpleNamespace(session_mode="clean", video_policy="failed", platform="android")
    appium_server = SimpleNamespace(url="http://127.0.0.1:4723")
    config = _FakeConfig()
    nodeid = "tests/unit/test_retry.py::test_keeps_driver"

    driver_obj = MagicMock()
    driver_obj.session_id = "session-123"
    recorder = MagicMock()

    monkeypatch.setattr(pytest_plugin, "_build_final_config", lambda *a, **k: object())
    monkeypatch.setattr(pytest_plugin, "create_driver", MagicMock(return_value=driver_obj))
    monkeypatch.setattr(pytest_plugin, "ScreenRecorder", MagicMock(return_value=recorder))

    first_req = _FakeRequest(config, _FakeNode(nodeid))
    first_gen = pytest_plugin.driver.__wrapped__(
        settings, appium_server, None, None, first_req
    )
    assert next(first_gen) is driver_obj
    first_req.node.stash[pytest_plugin.KEEP_DRIVER_ALIVE_KEY] = True
    first_gen.close()

    assert config.stash[pytest_plugin.RETRY_DRIVER_REGISTRY_KEY][nodeid] is driver_obj
    assert config.stash[pytest_plugin.RETRY_RECORDER_REGISTRY_KEY][nodeid] is recorder
    driver_obj.quit.assert_not_called()

    second_req = _FakeRequest(config, _FakeNode(nodeid))
    second_gen = pytest_plugin.driver.__wrapped__(
        settings, appium_server, None, None, second_req
    )
    assert next(second_gen) is driver_obj
    assert second_req.node.stash[pytest_plugin.RECORDER_KEY] is recorder
    second_gen.close()

    assert nodeid not in config.stash[pytest_plugin.RETRY_DRIVER_REGISTRY_KEY]
    assert nodeid not in config.stash[pytest_plugin.RETRY_RECORDER_REGISTRY_KEY]
    driver_obj.quit.assert_called_once()


def test_pytest_configure_wraps_unknown_override_as_usage_error(monkeypatch) -> None:
    config = _FakeConfig()

    monkeypatch.setattr(pytest_plugin, "load_settings", lambda env_file=None: object())

    def _raise_unknown(_settings, _overrides):
        raise ValueError("Unknown appium-pytest-kit setting override(s): 'unknownField'")

    monkeypatch.setattr(pytest_plugin, "apply_cli_overrides", _raise_unknown)

    with pytest.raises(pytest.UsageError, match="Unknown appium-pytest-kit setting"):
        pytest_plugin.pytest_configure(config)  # type: ignore[arg-type]


def test_build_final_config_rejects_unknown_capability_in_strict_mode(monkeypatch) -> None:
    settings = SimpleNamespace(strict_config=True)
    appium_server = SimpleNamespace(url="http://127.0.0.1:4723")

    hook = SimpleNamespace(
        pytest_appium_pytest_kit_capabilities=lambda **kwargs: [{"totallyUnknownCap": True}]
    )
    request = SimpleNamespace(config=SimpleNamespace(pluginmanager=SimpleNamespace(hook=hook)))

    monkeypatch.setattr(pytest_plugin, "validate_launch_config", lambda _settings: None)
    monkeypatch.setattr(
        pytest_plugin,
        "build_driver_config",
        lambda _settings, server_url: SimpleNamespace(
            server_url=server_url,
            capabilities={"platformName": "android"},
            implicit_wait=0.0,
        ),
    )

    with pytest.raises(ConfigurationError, match="unknown capability key"):
        pytest_plugin._build_final_config(settings, appium_server, request)


def test_apply_device_info_overwrites_empty_capabilities() -> None:
    capabilities = {"deviceName": "", "udid": "  ", "platformVersion": None}
    info = DeviceInfo(
        device_name="Pixel 8",
        platform_name="android",
        udid="emulator-5554",
        platform_version="14",
    )

    pytest_plugin._apply_device_info(capabilities, info)

    assert capabilities["deviceName"] == "Pixel 8"
    assert capabilities["udid"] == "emulator-5554"
    assert capabilities["platformVersion"] == "14"


def test_build_final_config_uses_profile_automation_name_when_default(monkeypatch) -> None:
    settings = SimpleNamespace(strict_config=False, platform="android", automation_name=None)
    appium_server = SimpleNamespace(url="http://127.0.0.1:4723")

    hook = SimpleNamespace(pytest_appium_pytest_kit_capabilities=lambda **kwargs: [])
    request = SimpleNamespace(config=SimpleNamespace(pluginmanager=SimpleNamespace(hook=hook)))

    monkeypatch.setattr(pytest_plugin, "validate_launch_config", lambda _settings: None)
    monkeypatch.setattr(
        pytest_plugin,
        "build_driver_config",
        lambda _settings, server_url: SimpleNamespace(
            server_url=server_url,
            capabilities={"platformName": "android", "automationName": "UiAutomator2"},
            implicit_wait=0.0,
        ),
    )

    info = DeviceInfo(
        device_name="Pixel 7",
        platform_name="android",
        automation_name="Espresso",
    )
    config = pytest_plugin._build_final_config(settings, appium_server, request, info=info)
    assert config.capabilities["automationName"] == "Espresso"
