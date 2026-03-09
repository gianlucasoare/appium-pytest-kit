---
name: appium-kit-test-runner
description: Run appium-pytest-kit lint and test lanes and summarize the results. Use when you need deterministic execution of targeted tests, the full suite, CI-equivalent lanes, or concise reporting of failures, warnings, and first-traceback context.
---

# Appium Kit Test Runner

Run the smallest useful lane first, then expand only when it earns you confidence.

## Commands

- Full suite: `python3 -m pytest -q`
- Targeted file: `python3 -m pytest -q tests/unit/<file>`
- Main lane: `python3 -m pytest -q -m "not quarantine"`
- Quarantine lane: `python3 -m pytest -q -m quarantine`
- xdist lane: `python3 -m pytest -q -n 2 -m "not quarantine"`
- Lint: `python3 -m ruff check .`

## Reporting Rules

1. Report total passed, failed, skipped, and warnings.
2. Surface the first real failure with traceback context.
3. Classify the likely cause as code bug, test bug, environment issue, or flaky behavior.
4. Call out new warnings or unexpected collection changes.
5. Keep the summary concise and actionable.

## Use Pattern

- Start with the narrowest command that answers the question.
- If a targeted run fails, do not jump to the full suite until the local failure is understood.
- If a broad lane fails, identify the first real failure before speculating.
