#!/usr/bin/env python3
"""Generate and prepend a release section in CHANGELOG.md from git history."""


from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
from pathlib import Path

_CATEGORY_ORDER = ("Added", "Fixed", "Changed")
_CATEGORY_MAP = {
    "feat": "Added",
    "fix": "Fixed",
    "perf": "Changed",
    "refactor": "Changed",
    "docs": "Changed",
    "test": "Changed",
    "chore": "Changed",
    "build": "Changed",
    "ci": "Changed",
    "style": "Changed",
}


def _run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _discover_previous_tag(current_tag: str | None) -> str | None:
    try:
        raw = _run_git(["tag", "--sort=-creatordate"])
    except subprocess.CalledProcessError:
        return None
    tags = [line.strip() for line in raw.splitlines() if line.strip()]
    for tag in tags:
        if current_tag and tag == current_tag:
            continue
        return tag
    return None


def _clean_subject(subject: str) -> str:
    cleaned = re.sub(r"^[a-zA-Z]+(?:\([^)]+\))?!?:\s*", "", subject).strip()
    return cleaned or subject.strip()


def _categorize_subject(subject: str) -> str:
    match = re.match(r"^([a-zA-Z]+)(?:\([^)]+\))?!?:", subject.strip())
    if match:
        return _CATEGORY_MAP.get(match.group(1).lower(), "Changed")
    return "Changed"


def _commit_rows(previous_tag: str | None, target_ref: str) -> list[tuple[str, str]]:
    revision = f"{previous_tag}..{target_ref}" if previous_tag else target_ref
    try:
        raw = _run_git(["log", "--pretty=format:%h%x1f%s%x1e", revision])
    except subprocess.CalledProcessError:
        return []

    rows: list[tuple[str, str]] = []
    for chunk in raw.split("\x1e"):
        chunk = chunk.strip()
        if not chunk or "\x1f" not in chunk:
            continue
        sha, subject = chunk.split("\x1f", 1)
        subject = subject.strip()
        if not subject or subject.startswith("Merge "):
            continue
        rows.append((sha.strip(), subject))
    return rows


def _format_release_section(
    *,
    version: str,
    date_text: str,
    previous_tag: str | None,
    target_ref: str,
    repo_url: str | None,
) -> str:
    categorized: dict[str, list[str]] = {key: [] for key in _CATEGORY_ORDER}
    for sha, subject in _commit_rows(previous_tag, target_ref):
        category = _categorize_subject(subject)
        cleaned = _clean_subject(subject)
        if repo_url:
            line = f"- {cleaned} ([`{sha}`]({repo_url}/commit/{sha}))"
        else:
            line = f"- {cleaned} (`{sha}`)"
        categorized[category].append(line)

    lines: list[str] = [f"## [{version}] - {date_text}", ""]
    if not any(categorized.values()):
        lines.extend(["### Changed", "", "- No user-facing changes captured.", ""])
        return "\n".join(lines).rstrip() + "\n"

    for category in _CATEGORY_ORDER:
        entries = categorized.get(category, [])
        if not entries:
            continue
        lines.append(f"### {category}")
        lines.append("")
        lines.extend(entries)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _ensure_changelog_shell(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return (
        "# Changelog\n\n"
        "All notable changes to this project will be documented in this file.\n\n"
        "## [Unreleased]\n\n"
    )


def _insert_release_section(content: str, release_section: str, version: str) -> str:
    section_header = f"## [{version}]"
    if section_header in content:
        return content

    marker = "## [Unreleased]"
    if marker not in content:
        content = content.rstrip() + "\n\n## [Unreleased]\n\n"

    marker_index = content.index(marker)
    marker_end = content.find("\n", marker_index)
    if marker_end == -1:
        marker_end = len(content)
    insert_at = marker_end + 1

    while insert_at < len(content) and content[insert_at] == "\n":
        insert_at += 1

    prefix = content[:insert_at]
    suffix = content[insert_at:]
    if prefix and not prefix.endswith("\n\n"):
        prefix = prefix.rstrip("\n") + "\n\n"
    if suffix and not suffix.startswith("\n"):
        suffix = "\n" + suffix
    return f"{prefix}{release_section}{suffix}".rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Release version without leading 'v'.")
    parser.add_argument("--tag", default=None, help="Release tag (defaults to v<version>).")
    parser.add_argument(
        "--previous-tag",
        default=None,
        help="Override start tag for commit range. Auto-detected when omitted.",
    )
    parser.add_argument(
        "--target-ref",
        default="HEAD",
        help="Range end reference for git log (default: HEAD).",
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Release date in YYYY-MM-DD (default: today).",
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Changelog path (default: CHANGELOG.md).",
    )
    parser.add_argument(
        "--repo-url",
        default=None,
        help="Repository URL for commit links. Autodetected from GITHUB_SERVER_URL and "
        "GITHUB_REPOSITORY when available.",
    )
    args = parser.parse_args()

    version = args.version.strip().lstrip("v")
    tag = args.tag.strip() if args.tag else f"v{version}"
    previous_tag = args.previous_tag or _discover_previous_tag(tag)
    repo_url = args.repo_url
    if repo_url is None:
        gh_host = os.environ.get("GITHUB_SERVER_URL")
        gh_repo = os.environ.get("GITHUB_REPOSITORY")
        if gh_host and gh_repo:
            repo_url = f"{gh_host.rstrip('/')}/{gh_repo.strip('/')}"

    path = Path(args.changelog)
    content = _ensure_changelog_shell(path)
    release_section = _format_release_section(
        version=version,
        date_text=args.date,
        previous_tag=previous_tag,
        target_ref=args.target_ref,
        repo_url=repo_url,
    )
    updated = _insert_release_section(content, release_section, version)
    path.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
