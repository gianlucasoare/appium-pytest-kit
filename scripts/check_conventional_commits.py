#!/usr/bin/env python3
"""Validate commit subjects against Conventional Commits."""


from __future__ import annotations

import argparse
import re
import subprocess

CONVENTIONAL_SUBJECT_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([^)]+\))?(!)?: .+"
)


def _git_log_subjects(revision_range: str) -> list[tuple[str, str]]:
    try:
        raw = subprocess.check_output(
            ["git", "log", "--format=%H%x1f%s%x1e", revision_range],
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Unable to read commits for range '{revision_range}': {exc}") from exc

    rows: list[tuple[str, str]] = []
    for chunk in raw.split("\x1e"):
        chunk = chunk.strip()
        if not chunk or "\x1f" not in chunk:
            continue
        sha, subject = chunk.split("\x1f", 1)
        rows.append((sha.strip(), subject.strip()))
    return rows


def _is_allowed_non_conventional(subject: str) -> bool:
    return subject.startswith("Merge ") or subject.startswith("Revert ")


def validate_range(revision_range: str) -> list[tuple[str, str]]:
    invalid: list[tuple[str, str]] = []
    for sha, subject in _git_log_subjects(revision_range):
        if not subject:
            continue
        if _is_allowed_non_conventional(subject):
            continue
        if CONVENTIONAL_SUBJECT_RE.match(subject):
            continue
        invalid.append((sha, subject))
    return invalid


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--range",
        required=True,
        dest="revision_range",
        help="Git revision range to validate (e.g. origin/main..HEAD).",
    )
    args = parser.parse_args(argv)

    invalid = validate_range(args.revision_range)
    if not invalid:
        print("Conventional commit check passed.")
        return 0

    print("Conventional commit check failed for:")
    for sha, subject in invalid:
        print(f"- {sha[:12]}  {subject}")
    print(
        "\nExpected format: type(scope): subject  "
        "(type in feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
