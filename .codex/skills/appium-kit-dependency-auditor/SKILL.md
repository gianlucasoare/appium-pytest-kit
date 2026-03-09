---
name: appium-kit-dependency-auditor
description: Audit dependency declarations, extras groups, soft imports, and version bounds in appium-pytest-kit. Use when adding, removing, updating, or reviewing dependencies, optional extras, install behavior, or compatibility expectations for Python and pytest tooling.
---

# Appium Kit Dependency Auditor

Audit declared dependencies against actual repo usage and install behavior.

## Procedure

1. Read `pyproject.toml` first.
2. Inspect required dependencies, optional extras, and dev groups from the live file.
3. Check installed versions if the task needs environment truth.
4. Grep the codebase for imports and soft-import patterns.
5. Flag unused deps, phantom deps, hard imports of optional packages, and version-bound problems.
6. Verify that `[all]` remains the union of optional groups.

## Repo-Specific Expectations

- Core behavior should work without optional extras installed.
- Optional dependencies must degrade gracefully.
- Soft imports should use clear `ImportError` handling.
- New dependencies must be reflected in `docs/installation.md`.
- Avoid exact pins in this library package unless there is a hard compatibility reason.

## Deliverables

- Dependency health summary.
- Specific issues with severity.
- Concrete fix direction for declarations, imports, or docs.
