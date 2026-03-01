---
name: test-building
description: Skill for building high-value automated tests from risk, user flows, and data strategy, including fixture setup and assertion design.
---

# Test Building

## Use This Skill When

- Creating new test cases or suites.
- Expanding coverage for new features.
- Converting manual checks into automation.

## Design Process

1. Identify behavior and business risk.
2. Define preconditions and data model.
3. Write minimal reliable steps.
4. Add assertions for outcome and side effects.
5. Classify test (`smoke`, `regression`, `quarantine`).

## Test Quality Rules

- One core behavior per test.
- No hidden dependencies on test order.
- Assertions should reflect user/business value.
- Include cleanup strategy where needed.
