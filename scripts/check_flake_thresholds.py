#!/usr/bin/env python3
"""Fail when flake metrics exceed configured quality-gate thresholds."""


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


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _check_metric(
    *,
    label: str,
    actual: int,
    limit: int | None,
    violations: list[str],
) -> None:
    if limit is None:
        return
    if actual > limit:
        violations.append(f"{label}={actual} exceeded max={limit}")


def evaluate_thresholds(
    summary_payload: dict[str, Any],
    trend_payload: dict[str, Any] | None,
    *,
    max_flaky_tests: int | None,
    max_final_failed_after_retries: int | None,
    max_tests_with_retries: int | None,
    max_retries_executed_total: int | None,
    max_delta_flaky_tests: int | None,
    max_delta_retries_executed_total: int | None,
) -> list[str]:
    summary = summary_payload.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}

    violations: list[str] = []
    _check_metric(
        label="summary.flaky_tests",
        actual=_to_int(summary.get("flaky_tests")),
        limit=max_flaky_tests,
        violations=violations,
    )
    _check_metric(
        label="summary.final_failed_after_retries",
        actual=_to_int(summary.get("final_failed_after_retries")),
        limit=max_final_failed_after_retries,
        violations=violations,
    )
    _check_metric(
        label="summary.tests_with_retries",
        actual=_to_int(summary.get("tests_with_retries")),
        limit=max_tests_with_retries,
        violations=violations,
    )
    _check_metric(
        label="summary.retries_executed_total",
        actual=_to_int(summary.get("retries_executed_total")),
        limit=max_retries_executed_total,
        violations=violations,
    )

    if trend_payload is None:
        return violations
    trend = trend_payload.get("trend", {})
    if not isinstance(trend, dict):
        return violations
    delta = trend.get("delta_from_previous", {})
    if not isinstance(delta, dict):
        return violations

    _check_metric(
        label="trend.delta_from_previous.flaky_tests",
        actual=_to_int(delta.get("flaky_tests")),
        limit=max_delta_flaky_tests,
        violations=violations,
    )
    _check_metric(
        label="trend.delta_from_previous.retries_executed_total",
        actual=_to_int(delta.get("retries_executed_total")),
        limit=max_delta_retries_executed_total,
        violations=violations,
    )
    return violations


def _non_negative(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be >= 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("artifacts/appium-pytest-kit/flake-summary.json"),
        help="Path to flake-summary.json",
    )
    parser.add_argument(
        "--trend",
        type=Path,
        default=Path("artifacts/appium-pytest-kit/flake-trend.json"),
        help="Path to flake-trend.json (optional; ignored when missing)",
    )
    parser.add_argument("--max-flaky-tests", type=_non_negative, default=0)
    parser.add_argument("--max-final-failed-after-retries", type=_non_negative, default=0)
    parser.add_argument("--max-tests-with-retries", type=_non_negative, default=0)
    parser.add_argument("--max-retries-executed-total", type=_non_negative, default=0)
    parser.add_argument(
        "--max-delta-flaky-tests",
        type=_non_negative,
        default=None,
    )
    parser.add_argument(
        "--max-delta-retries-executed-total",
        type=_non_negative,
        default=None,
    )
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
        max_flaky_tests=args.max_flaky_tests,
        max_final_failed_after_retries=args.max_final_failed_after_retries,
        max_tests_with_retries=args.max_tests_with_retries,
        max_retries_executed_total=args.max_retries_executed_total,
        max_delta_flaky_tests=args.max_delta_flaky_tests,
        max_delta_retries_executed_total=args.max_delta_retries_executed_total,
    )
    if violations:
        print("Flake quality gate failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1
    print("Flake quality gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
