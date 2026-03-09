---
name: appium-kit-release
description: Prepare appium-pytest-kit releases and release-adjacent quality gates. Use when bumping versions, checking backward compatibility, updating changelog entries, tuning flake or performance thresholds, reviewing release workflows, or planning the steps required before tagging or publishing.
---

# Appium Kit Release

Treat release work as policy plus evidence. Use live repo state to decide whether the package is ready, not assumptions carried over from earlier runs.

## Release Preparation

1. Read `pyproject.toml`, `CHANGELOG.md`, and the relevant workflow files.
2. Classify the change as patch, minor, or major.
3. Confirm versioning, migration notes, and deprecation expectations match that classification.
4. Run or plan the mandatory preflight sequence from the root `AGENTS.md`.
5. Verify release automation still matches the repo policy.

## Quality Gates

- Flake thresholds live in `scripts/check_flake_thresholds.py`.
- Performance thresholds live in `scripts/check_perf_thresholds.py`.
- Prefer historical trend inputs over one-off numbers when changing thresholds.
- Use p95 or similarly robust metrics, not averages, when deciding whether a gate should fail builds.

## Compatibility Checks

- Inspect live public exports, fixture names, hook signatures, settings fields, and CLI flags before calling a change backward compatible.
- Treat `_internal/` changes as patch-level unless they leak into public behavior.
- If a breaking change is necessary, require deprecation handling, migration notes, changelog updates, and the matching major-version intent.

## Done

- Versioning and compatibility story are coherent.
- Quality gate changes are measurable and justified.
- Release prerequisites are explicit and verified.
