---
name: appium-kit-debugger
description: Systematically reproduce, isolate, fix, and regression-test appium-pytest-kit failures. Use when you are actively debugging a concrete failing test, command, hook, fixture, or runtime path and need an execution-focused playbook instead of a general review.
---

# Appium Kit Debugger

Use this as the execution loop once a concrete failure is in hand.

## Debug Procedure

1. Capture the full failing context.
2. Reproduce with the smallest deterministic command.
3. Narrow the fault by changing one variable at a time.
4. Fix the true fault boundary, not the symptom.
5. Add or update regression coverage.
6. Re-run the impacted lane, then broaden validation as needed.

## Preferred Commands

- Full suite: `python3 -m pytest -q`
- Targeted test: `python3 -m pytest -q tests/unit/<file>::<test>`
- Verbose targeted test: `python3 -m pytest -v tests/unit/<file>::<test>`
- Lint: `python3 -m ruff check .`

## Rules

- Do not keep broad debug instrumentation after the root cause is understood.
- Do not hide signal with catch-all exception handling or retry-only fixes.
- Preserve unrelated behavior and public contracts.
- Start from the first real traceback every time the failure output is noisy.

## Deliverables

- Root cause summary.
- Fix summary.
- Regression proof.
