---
name: appium-kit-code-reviewer
description: Perform severity-ordered code review for appium-pytest-kit. Use when reviewing diffs, pull requests, or local changes for correctness, regressions, xdist safety, backward compatibility, security, and missing tests before merge or release.
---

# Appium Kit Code Reviewer

Review changed code for risk before discussing style. Findings come first, summary later.

## Review Order

1. Check correctness and runtime failure paths.
2. Check behavioral regressions and edge cases.
3. Check concurrency, lifecycle, and xdist safety.
4. Check security and sensitive-data handling.
5. Check missing tests, missing docs, and observability gaps.
6. Note maintainability issues only after functional risk is covered.

## Severity Levels

- `P0`: release-blocking safety, security, corruption, or data-loss issue.
- `P1`: high-risk functional bug or regression.
- `P2`: medium-risk reliability or compatibility gap.
- `P3`: low-risk cleanup or clarity issue.

## Review Rules

- Read the changed files and enough surrounding code to understand intent.
- Cite concrete failure modes and fix direction, not vague opinions.
- Check public API changes for backward-compatibility impact.
- Check fixture, hook, and reporting changes for xdist behavior.
- If no findings are present, say so explicitly and mention residual risk or validation gaps.

## Output

- Present findings first, sorted by severity.
- Include file references, impact, and concrete fix direction.
- Keep summary brief and secondary.
