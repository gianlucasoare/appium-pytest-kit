"""Tests for CI/release helper scripts."""


from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_script_module(script_name: str):
    root = Path(__file__).resolve().parents[2]
    path = root / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(script_name.replace(".py", ""), path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_flake_thresholds_reports_violation() -> None:
    module = _load_script_module("check_flake_thresholds.py")
    summary_payload = {
        "summary": {
            "flaky_tests": 2,
            "final_failed_after_retries": 1,
            "tests_with_retries": 3,
            "retries_executed_total": 4,
        }
    }
    trend_payload = {
        "trend": {
            "delta_from_previous": {
                "flaky_tests": 1,
                "retries_executed_total": 2,
            }
        }
    }

    violations = module.evaluate_thresholds(
        summary_payload,
        trend_payload,
        max_flaky_tests=0,
        max_final_failed_after_retries=0,
        max_tests_with_retries=0,
        max_retries_executed_total=0,
        max_delta_flaky_tests=0,
        max_delta_retries_executed_total=0,
    )

    assert violations
    assert any("summary.flaky_tests" in row for row in violations)
    assert any("trend.delta_from_previous.flaky_tests" in row for row in violations)


def test_conventional_commit_validation_accepts_and_rejects(monkeypatch) -> None:
    module = _load_script_module("check_conventional_commits.py")
    monkeypatch.setattr(
        module,
        "_git_log_subjects",
        lambda _range: [
            ("a" * 40, "feat(ci): add gate"),
            ("b" * 40, "fix: resolve bug"),
            ("c" * 40, "bad commit subject"),
            ("d" * 40, "Merge pull request #1 from demo"),
        ],
    )

    invalid = module.validate_range("HEAD~4..HEAD")
    assert len(invalid) == 1
    assert invalid[0][1] == "bad commit subject"


def test_perf_thresholds_reports_violation() -> None:
    module = _load_script_module("check_perf_thresholds.py")
    summary_payload = {
        "summary": {
            "test_ms_p95": 3000.0,
            "action_ms_p95": 1200.0,
            "session_start_ms_p95": 9000.0,
            "budget_violations": 2,
        }
    }
    trend_payload = {
        "trend": {
            "delta_from_previous": {
                "test_ms_p95": 150.0,
                "action_ms_p95": 40.0,
            }
        }
    }

    violations = module.evaluate_thresholds(
        summary_payload,
        trend_payload,
        max_test_ms_p95=2000.0,
        max_action_ms_p95=1000.0,
        max_session_start_ms_p95=5000.0,
        max_budget_violations=0,
        max_delta_test_ms_p95=100.0,
        max_delta_action_ms_p95=10.0,
    )

    assert violations
    assert any("summary.test_ms_p95" in row for row in violations)
    assert any("trend.delta_from_previous.test_ms_p95" in row for row in violations)
