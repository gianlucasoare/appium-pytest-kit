---
name: code-review
description: Structured code review with severity-ordered findings focused on correctness, regression risk, and test coverage.
---

# Code Review

## Use This Skill When

- Reviewing pull requests or commits
- Auditing changed files for bugs and risk
- Validating test coverage and behavior safety

## Review Order

1. Correctness and runtime failures
2. Behavioral regressions and edge cases
3. Concurrency/state/lifecycle risks
4. Security and data exposure issues
5. Test gaps and observability gaps
6. Maintainability concerns (only after functional risk)

## Output Format

Findings first, sorted by severity. Each finding includes:
- File and line reference
- Impact and failure mode
- Concrete fix direction

Then open questions/assumptions. Short summary only after issues are listed.

## Severity Guide

- **P0**: release-blocking — data loss, security, corruption
- **P1**: high-risk functional bug or regression
- **P2**: medium risk or reliability gap
- **P3**: low-risk cleanup or clarity issue

## Rules

- Be explicit; avoid vague comments like "consider improving"
- Prefer reproducible evidence over opinion
- If no issues found, state that clearly and note residual risks
- Check backward compatibility for public API changes
- Verify xdist safety for any fixture or hook changes
