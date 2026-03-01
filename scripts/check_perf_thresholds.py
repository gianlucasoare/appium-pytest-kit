#!/usr/bin/env python3
"""Validate performance budgets from perf-summary/perf-trend artifacts."""


from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Unable to read JSON file: {path} ({exc})") from exc
    except ValueError as exc:
        raise SystemExit(f"Invalid JSON payload: {path} ({exc})") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return payload


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _check_upper_bound(
    *,
    label: str,
    actual: float,
    limit: float | None,
    violations: list[str],
) -> None:
    if limit is None:
        return
    if actual > float(limit):
        violations.append(f"{label}={actual:.3f} exceeded max={float(limit):.3f}")


def evaluate_thresholds(
    summary_payload: dict[str, Any],
    trend_payload: dict[str, Any] | None,
    *,
    max_test_ms_p95: float | None,
    max_action_ms_p95: float | None,
    max_session_start_ms_p95: float | None,
    max_budget_violations: int | None,
    max_delta_test_ms_p95: float | None,
    max_delta_action_ms_p95: float | None,
) -> list[str]:
    summary = summary_payload.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    violations: list[str] = []
    _check_upper_bound(
        label="summary.test_ms_p95",
        actual=_to_float(summary.get("test_ms_p95")),
        limit=max_test_ms_p95,
        violations=violations,
    )
    _check_upper_bound(
        label="summary.action_ms_p95",
        actual=_to_float(summary.get("action_ms_p95")),
        limit=max_action_ms_p95,
        violations=violations,
    )
    _check_upper_bound(
        label="summary.session_start_ms_p95",
        actual=_to_float(summary.get("session_start_ms_p95")),
        limit=max_session_start_ms_p95,
        violations=violations,
    )
    if max_budget_violations is not None:
        budget_violations = int(_to_float(summary.get("budget_violations")))
        if budget_violations > max_budget_violations:
            violations.append(
                "summary.budget_violations="
                f"{budget_violations} exceeded max={max_budget_violations}"
            )

    if trend_payload is None:
        return violations
    trend = trend_payload.get("trend", {})
    if not isinstance(trend, dict):
        return violations
    delta = trend.get("delta_from_previous", {})
    if not isinstance(delta, dict):
        return violations

    _check_upper_bound(
        label="trend.delta_from_previous.test_ms_p95",
        actual=_to_float(delta.get("test_ms_p95")),
        limit=max_delta_test_ms_p95,
        violations=violations,
    )
    _check_upper_bound(
        label="trend.delta_from_previous.action_ms_p95",
        actual=_to_float(delta.get("action_ms_p95")),
        limit=max_delta_action_ms_p95,
        violations=violations,
    )
    return violations


def _non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be >= 0")
    return parsed


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be >= 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("artifacts/appium-pytest-kit/perf-summary.json"),
        help="Path to perf-summary.json",
    )
    parser.add_argument(
        "--trend",
        type=Path,
        default=Path("artifacts/appium-pytest-kit/perf-trend.json"),
        help="Path to perf-trend.json (optional; ignored when missing)",
    )
    parser.add_argument("--max-test-ms-p95", type=_non_negative_float, default=None)
    parser.add_argument("--max-action-ms-p95", type=_non_negative_float, default=None)
    parser.add_argument("--max-session-start-ms-p95", type=_non_negative_float, default=None)
    parser.add_argument("--max-budget-violations", type=_non_negative_int, default=None)
    parser.add_argument("--max-delta-test-ms-p95", type=_non_negative_float, default=None)
    parser.add_argument("--max-delta-action-ms-p95", type=_non_negative_float, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.summary.exists():
        raise SystemExit(f"Required summary file not found: {args.summary}")
    summary_payload = _load_json(args.summary)
    trend_payload = _load_json(args.trend) if args.trend.exists() else None

    violations = evaluate_thresholds(
        summary_payload,
        trend_payload,
        max_test_ms_p95=args.max_test_ms_p95,
        max_action_ms_p95=args.max_action_ms_p95,
        max_session_start_ms_p95=args.max_session_start_ms_p95,
        max_budget_violations=args.max_budget_violations,
        max_delta_test_ms_p95=args.max_delta_test_ms_p95,
        max_delta_action_ms_p95=args.max_delta_action_ms_p95,
    )
    if violations:
        print("Performance quality gate failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print("Performance quality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
