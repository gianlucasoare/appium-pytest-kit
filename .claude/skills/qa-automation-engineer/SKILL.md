---
name: qa-automation-engineer
description: End-to-end QA automation engineering for mobile/web test design, stabilization, diagnostics, and CI reliability.
---

# QA Automation Engineer

## Use This Skill When

- Building or refactoring automated tests
- Improving flake rate, diagnostics, or CI stability
- Designing regression/smoke suites and execution strategy

## Workflow

1. Define intent: user behavior, risk, critical path
2. Choose layer: UI test, API setup, fixture helper
3. Design deterministic setup/teardown
4. Implement clear assertions and failure context
5. Add diagnostics and reporting artifacts
6. Validate locally, then in CI lanes

## Quality Criteria

- Test is independent and repeatable
- Selectors are stable and maintainable
- Failure message explains what and why
- Flaky behavior has explicit mitigation

## Anti-Patterns

- Hard sleeps as synchronization strategy
- Hidden shared state between tests
- Assertions without actionable context
