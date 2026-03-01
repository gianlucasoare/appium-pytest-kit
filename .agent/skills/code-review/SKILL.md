---
name: code-review
description: Skill for high-signal code review focused on correctness, regression risk, reliability, and missing tests, with severity-ordered findings.
---

# Code Review

## Use This Skill When

- Reviewing pull requests or commits.
- Auditing changed files for bugs and risk.
- Validating test coverage and behavior safety.

## Review Order

1. Correctness and runtime failures.
2. Behavioral regressions and edge cases.
3. Concurrency/state/lifecycle risks.
4. Security and data exposure issues.
5. Test gaps and observability gaps.
6. Maintainability concerns (only after functional risk).

## Output Format

- Findings first, sorted by severity.
- Each finding includes:
  - file and line reference
  - impact and failure mode
  - concrete fix direction
- After findings, include open questions/assumptions.
- Provide short summary only after issues are listed.

## Severity Guide

- P0: release-blocking, data loss/security/corruption
- P1: high-risk functional bug or regression
- P2: medium risk or reliability gap
- P3: low-risk cleanup or clarity issue

## Review Rules

- Be explicit; avoid vague comments.
- Prefer reproducible evidence over opinion.
- If no issues found, state that clearly and note residual risks.
