---
name: release-and-ci
description: Skill for CI design, release hardening, version/tag validation, changelog automation, and safe PyPI publishing workflows.
---

# Release And CI

## Use This Skill When

- Updating GitHub workflows.
- Preparing package releases.
- Hardening quality gates for merge/publish.

## Release Pipeline Requirements

- Test and lint before artifact build.
- Validate version/tag consistency.
- Publish only from trusted tag refs.
- Generate release notes/changelog automatically.

## CI Requirements

- Main lane for core tests.
- Optional lanes for extras/parallel paths.
- Dedicated non-blocking quarantine lane.
- Explicit quality gates (flake/perf/security as needed).
