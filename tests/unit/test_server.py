"""Tests for Appium server manager preflight behavior."""

import pytest

from appium_pytest_kit._internal.server import AppiumServerManager
from appium_pytest_kit.errors import ConfigurationError
from appium_pytest_kit.settings import AppiumPytestKitSettings


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        _ = (exc_type, exc, tb)
        return False

    def read(self) -> bytes:
        return self._payload


def test_status_endpoint_appends_status_preserving_base_path() -> None:
    settings = AppiumPytestKitSettings(
        appium_url="http://127.0.0.1:4723/wd/hub",
        manage_appium_server=False,
    )
    manager = AppiumServerManager(settings)
    endpoint = manager._status_endpoint(settings.appium_url)  # noqa: SLF001
    assert endpoint == "http://127.0.0.1:4723/wd/hub/status"


def test_resolve_unmanaged_runs_preflight_when_enabled(monkeypatch) -> None:
    settings = AppiumPytestKitSettings(
        appium_url="http://127.0.0.1:4723",
        manage_appium_server=False,
        appium_preflight_status=True,
    )
    monkeypatch.setattr(
        "appium_pytest_kit._internal.server.urlopen",
        lambda *_args, **_kwargs: _FakeResponse(b'{"value":{"ready":true}}'),
    )

    info = AppiumServerManager(settings).resolve()
    assert info.url == "http://127.0.0.1:4723"
    assert info.managed is False


def test_resolve_unmanaged_raises_when_preflight_reports_not_ready(monkeypatch) -> None:
    settings = AppiumPytestKitSettings(
        appium_url="http://127.0.0.1:4723",
        manage_appium_server=False,
        appium_preflight_status=True,
    )
    monkeypatch.setattr(
        "appium_pytest_kit._internal.server.urlopen",
        lambda *_args, **_kwargs: _FakeResponse(b'{"value":{"ready":false}}'),
    )

    with pytest.raises(ConfigurationError, match="ready=false"):
        AppiumServerManager(settings).resolve()


def test_resolve_unmanaged_skips_preflight_when_disabled(monkeypatch) -> None:
    settings = AppiumPytestKitSettings(
        appium_url="http://127.0.0.1:4723",
        manage_appium_server=False,
        appium_preflight_status=False,
    )

    def _fail(*_args, **_kwargs):
        raise AssertionError("urlopen should not be called when preflight is disabled")

    monkeypatch.setattr("appium_pytest_kit._internal.server.urlopen", _fail)
    info = AppiumServerManager(settings).resolve()
    assert info.managed is False
    assert info.url == "http://127.0.0.1:4723"


def test_managed_server_uses_worker_port_offset(monkeypatch) -> None:
    started: dict[str, object] = {}

    class _FakeService:
        def start(self, *, args, timeout_ms):
            started["args"] = args
            started["timeout_ms"] = timeout_ms

        @staticmethod
        def is_running() -> bool:
            return True

        @staticmethod
        def stop() -> None:
            return None

    settings = AppiumPytestKitSettings(
        manage_appium_server=True,
        appium_host="127.0.0.1",
        appium_port=4723,
        appium_base_path="/wd/hub",
    )
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw3")
    monkeypatch.setattr(
        "appium.webdriver.appium_service.AppiumService",
        lambda: _FakeService(),
    )

    manager = AppiumServerManager(settings)
    info = manager.resolve()

    assert "--port" in started["args"]
    assert "4726" in started["args"]
    assert info.url == "http://127.0.0.1:4726/wd/hub"
    assert info.managed is True
