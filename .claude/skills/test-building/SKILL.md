---
name: test-building
description: Build high-value automated tests with risk-based design, fixture strategy, assertion rigor, and marker classification.
---

# Test Building

## Use This Skill When

- Creating new test cases or suites
- Expanding coverage for new features
- Converting manual checks into automation
- Refactoring existing tests for reliability

## Design Process

1. Identify behavior under test and business risk
2. Define preconditions and data model
3. Choose fixtures and data setup strategy
4. Write minimal reliable steps using robust selectors and explicit waits
5. Add assertions for outcome and side effects
6. Capture diagnostics on failure paths
7. Classify test: `smoke`, `regression`, or `quarantine`

## Test Quality Rules

- One core behavior per test
- No hidden dependencies on test order
- Assertions should reflect user/business value
- Include cleanup strategy where needed
- Failure output must be actionable (include locator, timeout, expected vs actual)
- Use explicit waits, never hard sleeps

## Anti-Patterns

- Hard sleeps as synchronization strategy
- Hidden shared state between tests
- Assertions without actionable context
- Tests that pass but don't validate meaningful behavior

## Definition of Done

- Test is deterministic and repeatable
- Failure output is actionable
- Runtime and scope are appropriate for its classification
- Marker assigned (`smoke`, `regression`, `quarantine`)
