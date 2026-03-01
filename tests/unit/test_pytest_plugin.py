"""Targeted tests for pytest plugin lifecycle and option wiring."""

import json
from pathlib import Path
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
        self.workerinput = None
        self.pluginmanager = SimpleNamespace(
            hook=SimpleNamespace(
                pytest_appium_pytest_kit_driver_created=MagicMock(),
                pytest_appium_pytest_kit_configure_settings=MagicMock(return_value=None),
            ),
            hasplugin=lambda _name: False,
        )
        self._ini_markers: list[str] = []

    def getoption(self, name: str, default=None):
        if name == "app_override":
            return ["unknownField=1"]
        return default

    def addinivalue_line(self, _name: str, value: str) -> None:
        self._ini_markers.append(value)


class _ConfigureConfig:
    def __init__(self, *, workerinput=None, has_xdist: bool = False, options=None) -> None:
        self.workerinput = workerinput
        self._options = options or {}
        self.stash: dict = {}
        self.pluginmanager = SimpleNamespace(
            hook=SimpleNamespace(
                pytest_appium_pytest_kit_configure_settings=MagicMock(return_value=None),
            ),
            hasplugin=lambda name: has_xdist if name == "xdist" else False,
        )
        self._ini_markers: list[str] = []

    def getoption(self, name: str, default=None):
        if name == "app_override":
            return self._options.get(name, [])
        return self._options.get(name, default)

    def addinivalue_line(self, _name: str, value: str) -> None:
        self._ini_markers.append(value)


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


def test_cleanup_artifacts_dir_removes_existing_content(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    nested = artifacts / "screenshots"
    nested.mkdir(parents=True)
    (nested / "old.png").write_bytes(b"x")

    pytest_plugin._cleanup_artifacts_dir(artifacts)

    assert artifacts.exists()
    assert list(artifacts.iterdir()) == []


def test_apply_xdist_worker_isolation_android_sets_default_system_port() -> None:
    config = SimpleNamespace(workerinput={"workerid": "gw2"})
    settings = SimpleNamespace(platform="android")
    capabilities: dict[str, object] = {}

    pytest_plugin._apply_xdist_worker_isolation(capabilities, settings, config)
    assert capabilities["systemPort"] == 8202


def test_apply_xdist_worker_isolation_ios_respects_explicit_ports() -> None:
    config = SimpleNamespace(workerinput={"workerid": "gw1"})
    settings = SimpleNamespace(platform="ios")
    capabilities = {"wdaLocalPort": 9900}

    pytest_plugin._apply_xdist_worker_isolation(capabilities, settings, config)
    assert capabilities["wdaLocalPort"] == 9900
    assert capabilities["webkitDebugProxyPort"] == 27754


def test_xdist_worker_id_does_not_use_env_when_workerinput_is_explicit_none(monkeypatch) -> None:
    config = SimpleNamespace(workerinput=None)
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw7")
    assert pytest_plugin._xdist_worker_id(config) is None


def test_xdist_worker_id_uses_env_when_workerinput_attribute_is_missing(monkeypatch) -> None:
    config = SimpleNamespace()
    monkeypatch.setenv("PYTEST_XDIST_WORKER", "gw3")
    assert pytest_plugin._xdist_worker_id(config) == "gw3"


def test_merge_xdist_worker_reports_writes_merged_summary(tmp_path: Path) -> None:
    report_dir = tmp_path / "report"
    worker_a = report_dir / "workers" / "gw0"
    worker_b = report_dir / "workers" / "gw1"
    worker_a.mkdir(parents=True)
    worker_b.mkdir(parents=True)

    (worker_a / "summary.json").write_text(
        json.dumps(
            {
                "totals": {"passed": 1, "failed": 0, "skipped": 0},
                "tests": [{"nodeid": "a::test_one", "outcome": "passed", "duration": 1.0}],
            }
        ),
        encoding="utf-8",
    )
    (worker_b / "summary.json").write_text(
        json.dumps(
            {
                "totals": {"passed": 0, "failed": 1, "skipped": 0},
                "tests": [{"nodeid": "b::test_two", "outcome": "failed", "duration": 1.5}],
            }
        ),
        encoding="utf-8",
    )

    merged_path = pytest_plugin._merge_xdist_worker_reports(report_dir)
    assert merged_path == report_dir / "summary.json"
    merged = json.loads((report_dir / "summary.json").read_text(encoding="utf-8"))
    assert merged["totals"] == {"passed": 1, "failed": 1, "skipped": 0}
    assert len(merged["tests"]) == 2


def test_merge_xdist_flake_reports_writes_merged_summary(tmp_path: Path) -> None:
    report_dir = tmp_path / "report"
    worker_a = report_dir / "workers" / "gw0"
    worker_b = report_dir / "workers" / "gw1"
    worker_a.mkdir(parents=True)
    worker_b.mkdir(parents=True)

    (worker_a / "flake-summary.json").write_text(
        json.dumps(
            {
                "summary": {"retries_executed_total": 1},
                "tests": [
                    {
                        "nodeid": "tests::flaky_a",
                        "failures": 1,
                        "max_retries": 2,
                        "final_outcome": "passed_after_retry",
                    }
                ],
                "flaky_tests": ["tests::flaky_a"],
                "final_failed_after_retries": [],
                "top_failure_signatures": [{"signature": "WaitTimeoutError", "count": 1}],
                "top_failing_locators": [{"locator": "id=btn_login", "count": 1}],
            }
        ),
        encoding="utf-8",
    )
    (worker_b / "flake-summary.json").write_text(
        json.dumps(
            {
                "summary": {"retries_executed_total": 2},
                "tests": [
                    {
                        "nodeid": "tests::flaky_b",
                        "failures": 2,
                        "max_retries": 2,
                        "final_outcome": "failed_after_retries",
                    }
                ],
                "flaky_tests": [],
                "final_failed_after_retries": ["tests::flaky_b"],
                "top_failure_signatures": [{"signature": "WaitTimeoutError", "count": 2}],
                "top_failing_locators": [{"locator": "id=btn_login", "count": 2}],
            }
        ),
        encoding="utf-8",
    )

    merged_path = pytest_plugin._merge_xdist_flake_reports(report_dir)
    assert merged_path == report_dir / "flake-summary.json"
    merged = json.loads((report_dir / "flake-summary.json").read_text(encoding="utf-8"))
    assert merged["summary"]["retries_executed_total"] == 3
    assert merged["summary"]["flaky_tests"] == 1
    assert merged["summary"]["final_failed_after_retries"] == 1
    assert merged["top_failure_signatures"][0]["count"] == 3
    assert merged["top_failing_locators"][0]["count"] == 3


def test_write_flake_trend_report_tracks_history_and_delta(tmp_path: Path) -> None:
    report_dir = tmp_path / "report"
    first_payload = {
        "summary": {
            "tests_with_retries": 1,
            "flaky_tests": 1,
            "final_failed_after_retries": 0,
            "retries_executed_total": 1,
        },
        "top_failure_signatures": [{"signature": "Timeout", "count": 1}],
        "top_failing_locators": [{"locator": "id=btn_login", "count": 1}],
    }
    second_payload = {
        "summary": {
            "tests_with_retries": 3,
            "flaky_tests": 2,
            "final_failed_after_retries": 1,
            "retries_executed_total": 4,
        },
        "top_failure_signatures": [{"signature": "NoSuchElement", "count": 2}],
        "top_failing_locators": [{"locator": "id=btn_submit", "count": 2}],
    }

    pytest_plugin._write_flake_trend_report(report_dir, first_payload, history_limit=10)
    trend_path = pytest_plugin._write_flake_trend_report(
        report_dir,
        second_payload,
        history_limit=10,
    )

    trend = json.loads(trend_path.read_text(encoding="utf-8"))
    assert trend["trend"]["runs_tracked"] == 2
    assert trend["trend"]["latest_summary"]["flaky_tests"] == 2
    assert trend["trend"]["previous_summary"]["flaky_tests"] == 1
    assert trend["trend"]["delta_from_previous"]["flaky_tests"] == 1
    assert trend["trend"]["delta_from_previous"]["retries_executed_total"] == 3
    assert len(trend["history"]) == 2


def test_prepare_perf_payload_summarizes_metrics() -> None:
    analytics = {
        "session_start_ms": [500.0, 700.0],
        "action_events": [
            {"nodeid": "tests::one", "action": "tap", "status": "ok", "duration_ms": 50.0},
            {"nodeid": "tests::one", "action": "type_text", "status": "ok", "duration_ms": 100.0},
        ],
        "tests": {
            "tests::one": {
                "outcome": "passed",
                "test_duration_ms": 1200.0,
                "action_count": 2,
                "action_total_ms": 150.0,
                "action_max_ms": 100.0,
                "action_p95_ms": 97.5,
            }
        },
        "budget_violations": [],
    }

    payload = pytest_plugin._prepare_perf_payload(analytics)

    assert payload["summary"]["tests_measured"] == 1
    assert payload["summary"]["action_events_total"] == 2
    assert payload["summary"]["action_ms_p95"] > 0
    assert payload["summary"]["test_ms_p95"] == 1200.0
    assert len(payload["slowest_actions"]) == 2


def test_write_perf_trend_report_tracks_history_and_delta(tmp_path: Path) -> None:
    report_dir = tmp_path / "report"
    first_payload = {
        "summary": {
            "tests_measured": 2,
            "action_events_total": 8,
            "budget_violations": 0,
            "session_start_ms_p95": 1200.0,
            "action_ms_p95": 400.0,
            "test_ms_p95": 5000.0,
        }
    }
    second_payload = {
        "summary": {
            "tests_measured": 3,
            "action_events_total": 12,
            "budget_violations": 1,
            "session_start_ms_p95": 1400.0,
            "action_ms_p95": 500.0,
            "test_ms_p95": 5500.0,
        }
    }

    pytest_plugin._write_perf_trend_report(report_dir, first_payload, history_limit=10)
    trend_path = pytest_plugin._write_perf_trend_report(
        report_dir,
        second_payload,
        history_limit=10,
    )
    trend = json.loads(trend_path.read_text(encoding="utf-8"))

    assert trend["trend"]["runs_tracked"] == 2
    assert trend["trend"]["latest_summary"]["budget_violations"] == 1
    assert trend["trend"]["delta_from_previous"]["action_ms_p95"] == 100.0


def test_merge_xdist_perf_reports_writes_merged_summary(tmp_path: Path) -> None:
    report_dir = tmp_path / "report"
    worker_a = report_dir / "workers" / "gw0"
    worker_b = report_dir / "workers" / "gw1"
    worker_a.mkdir(parents=True)
    worker_b.mkdir(parents=True)

    (worker_a / "perf-summary.json").write_text(
        json.dumps(
            {
                "summary": {},
                "session_start_ms": [500.0],
                "action_events": [
                    {
                        "nodeid": "tests::a",
                        "action": "tap",
                        "status": "ok",
                        "duration_ms": 60.0,
                    }
                ],
                "tests": [
                    {
                        "nodeid": "tests::a",
                        "outcome": "passed",
                        "test_duration_ms": 1000.0,
                        "action_count": 1,
                        "action_total_ms": 60.0,
                        "action_max_ms": 60.0,
                        "action_p95_ms": 60.0,
                    }
                ],
                "budget_violations": [],
            }
        ),
        encoding="utf-8",
    )
    (worker_b / "perf-summary.json").write_text(
        json.dumps(
            {
                "summary": {},
                "session_start_ms": [700.0],
                "action_events": [
                    {
                        "nodeid": "tests::b",
                        "action": "type_text",
                        "status": "ok",
                        "duration_ms": 90.0,
                    }
                ],
                "tests": [
                    {
                        "nodeid": "tests::b",
                        "outcome": "failed",
                        "test_duration_ms": 1300.0,
                        "action_count": 1,
                        "action_total_ms": 90.0,
                        "action_max_ms": 90.0,
                        "action_p95_ms": 90.0,
                    }
                ],
                "budget_violations": [
                    {"kind": "action_budget", "nodeid": "tests::b"}
                ],
            }
        ),
        encoding="utf-8",
    )

    merged_path = pytest_plugin._merge_xdist_perf_reports(report_dir)
    assert merged_path == report_dir / "perf-summary.json"
    payload = json.loads((report_dir / "perf-summary.json").read_text(encoding="utf-8"))
    assert payload["summary"]["tests_measured"] == 2
    assert payload["summary"]["action_events_total"] == 2
    assert payload["summary"]["budget_violations"] == 1


def test_warn_xdist_port_collisions_logs_warning(caplog) -> None:
    config = SimpleNamespace(workerinput={"workerid": "gw0"}, stash={})
    settings = SimpleNamespace(platform="android")
    capabilities = {"systemPort": 8200}

    with caplog.at_level("WARNING"):
        pytest_plugin._warn_xdist_port_collisions(capabilities, settings, config)

    assert "xdist:explicit_port" in caplog.text


def test_pytest_configure_skips_cleanup_in_xdist_worker(monkeypatch, tmp_path: Path) -> None:
    config = _ConfigureConfig(workerinput={"workerid": "gw0"}, has_xdist=True)
    settings = pytest_plugin.AppiumPytestKitSettings(
        clean_artifacts_on_start=True,
        artifacts_dir=tmp_path / "artifacts",
    )

    monkeypatch.setattr(pytest_plugin, "load_settings", lambda env_file=None: settings)
    monkeypatch.setattr(pytest_plugin, "apply_cli_overrides", lambda current, _overrides: current)
    cleanup_mock = MagicMock()
    monkeypatch.setattr(pytest_plugin, "_cleanup_artifacts_dir", cleanup_mock)

    pytest_plugin.pytest_configure(config)  # type: ignore[arg-type]
    cleanup_mock.assert_not_called()


def test_pytest_sessionfinish_merges_xdist_reports_on_controller(tmp_path: Path) -> None:
    report_dir = tmp_path / "report"
    worker_dir = report_dir / "workers" / "gw0"
    worker_dir.mkdir(parents=True)
    (worker_dir / "summary.json").write_text(
        json.dumps(
            {
                "tests": [{"nodeid": "tests::test_a", "outcome": "passed", "duration": 1.0}],
                "totals": {"passed": 1, "failed": 0, "skipped": 0},
            }
        ),
        encoding="utf-8",
    )
    (worker_dir / "flake-summary.json").write_text(
        json.dumps(
            {
                "summary": {
                    "tests_with_retries": 1,
                    "flaky_tests": 1,
                    "final_failed_after_retries": 0,
                    "retries_executed_total": 1,
                },
                "tests": [
                    {
                        "nodeid": "tests::test_a",
                        "failures": 1,
                        "max_retries": 1,
                        "final_outcome": "passed_after_retry",
                    }
                ],
                "flaky_tests": ["tests::test_a"],
                "final_failed_after_retries": [],
                "top_failure_signatures": [{"signature": "Timeout", "count": 1}],
                "top_failing_locators": [{"locator": "id=btn_login", "count": 1}],
            }
        ),
        encoding="utf-8",
    )
    (worker_dir / "perf-summary.json").write_text(
        json.dumps(
            {
                "summary": {
                    "tests_measured": 1,
                    "action_events_total": 1,
                    "budget_violations": 0,
                    "session_start_ms_p95": 900.0,
                    "action_ms_p95": 120.0,
                    "test_ms_p95": 1500.0,
                },
                "session_start_ms": [900.0],
                "action_events": [
                    {
                        "nodeid": "tests::test_a",
                        "action": "tap",
                        "status": "ok",
                        "duration_ms": 120.0,
                    }
                ],
                "tests": [
                    {
                        "nodeid": "tests::test_a",
                        "outcome": "passed",
                        "test_duration_ms": 1500.0,
                        "action_count": 1,
                        "action_total_ms": 120.0,
                        "action_max_ms": 120.0,
                        "action_p95_ms": 120.0,
                    }
                ],
                "slowest_actions": [],
                "budget_violations": [],
            }
        ),
        encoding="utf-8",
    )

    settings = pytest_plugin.AppiumPytestKitSettings(
        reporting_enabled=True,
        report_dir=report_dir,
        perf_enabled=True,
    )
    config = _ConfigureConfig(workerinput=None, has_xdist=True)
    config.stash[pytest_plugin.SETTINGS_KEY] = settings
    config.stash[pytest_plugin.REPORTER_KEY] = None
    config.stash[pytest_plugin.RETRY_DRIVER_REGISTRY_KEY] = {}
    config.stash[pytest_plugin.RETRY_RECORDER_REGISTRY_KEY] = {}

    session = SimpleNamespace(config=config)
    pytest_plugin.pytest_sessionfinish(session, 0)  # type: ignore[arg-type]

    merged_payload = json.loads((report_dir / "summary.json").read_text(encoding="utf-8"))
    assert merged_payload["totals"] == {"passed": 1, "failed": 0, "skipped": 0}
    merged_flake = json.loads((report_dir / "flake-summary.json").read_text(encoding="utf-8"))
    assert merged_flake["summary"]["flaky_tests"] == 1
    merged_trend = json.loads((report_dir / "flake-trend.json").read_text(encoding="utf-8"))
    assert merged_trend["trend"]["runs_tracked"] == 1
    merged_perf = json.loads((report_dir / "perf-summary.json").read_text(encoding="utf-8"))
    assert merged_perf["summary"]["tests_measured"] == 1
    perf_trend = json.loads((report_dir / "perf-trend.json").read_text(encoding="utf-8"))
    assert perf_trend["trend"]["runs_tracked"] == 1


def test_collection_modifyitems_skips_quarantine_when_mode_is_skip() -> None:
    class _Item:
        def __init__(self, has_quarantine: bool) -> None:
            self._has_quarantine = has_quarantine
            self.applied: list = []

        def get_closest_marker(self, name: str):
            if name == "quarantine" and self._has_quarantine:
                return object()
            return None

        def add_marker(self, marker) -> None:
            self.applied.append(marker)

    config = _ConfigureConfig()
    config.stash[pytest_plugin.SETTINGS_KEY] = pytest_plugin.AppiumPytestKitSettings(
        quarantine_mode="skip"
    )
    quarantined = _Item(has_quarantine=True)
    regular = _Item(has_quarantine=False)

    pytest_plugin.pytest_collection_modifyitems(config, [quarantined, regular])  # type: ignore[arg-type]

    assert quarantined.applied, "quarantined item should receive skip marker"
    assert regular.applied == []


def test_collection_modifyitems_keeps_quarantine_when_mode_is_run() -> None:
    class _Item:
        def __init__(self) -> None:
            self.applied: list = []

        def get_closest_marker(self, _name: str):
            return object()

        def add_marker(self, marker) -> None:
            self.applied.append(marker)

    config = _ConfigureConfig()
    config.stash[pytest_plugin.SETTINGS_KEY] = pytest_plugin.AppiumPytestKitSettings(
        quarantine_mode="run"
    )
    item = _Item()

    pytest_plugin.pytest_collection_modifyitems(config, [item])  # type: ignore[arg-type]

    assert item.applied == []
