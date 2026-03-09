---
name: appium-kit-debug
description: Diagnose failing or flaky behavior in appium-pytest-kit. Use when a unit test, CI lane, xdist path, reporting artifact, CLI flow, or intermittent automation behavior fails and you need fast triage, local reproduction, stabilization, and regression protection.
---

# Appium Kit Debug

Treat debugging as evidence gathering first, patching second. Keep the loop small until the fault is isolated.

## Triage Loop

1. Capture the first real traceback or failing assertion, not the summary line.
2. Classify the failure: code regression, flaky test, environment issue, or workflow configuration.
3. Reproduce with the smallest deterministic local command.
4. Narrow one layer at a time: config, plugin, fixture, action, reporting, workflow.
5. Form one hypothesis at a time and validate it quickly.
6. Add a regression test or lock in the failure before finalizing the fix.

## Lane Mapping

- Main lane: `python3 -m pytest -q -m "not quarantine"`
- Quarantine lane: `python3 -m pytest -q -m quarantine`
- xdist lane: `python3 -m pytest -q -n 2 -m "not quarantine"`
- Full suite: `python3 -m pytest -q`

## Failure Patterns To Check

- Missing worker artifacts or merge assumptions in xdist code paths.
- Shared mutable state or order dependence in tests.
- Optional dependency behavior when extras are not installed.
- Reporting and diagnostics code that assumes files always exist.
- Flaky selectors, timing, or retry interactions in automation-facing tests.

## Done

- Root cause is confirmed, not inferred.
- Fix lands at the real boundary.
- Regression coverage or quarantine follow-up is in place.
- The affected lane has been rerun.
