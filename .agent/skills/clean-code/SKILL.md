---
name: clean-code
description: Skill for writing and refactoring clean, maintainable code with clear naming, small units, explicit error handling, and test-backed behavior.
---

# Clean Code

## Use This Skill When

- Implementing new modules or APIs.
- Refactoring legacy code without changing behavior.
- Reviewing pull requests for readability and maintainability.

## Core Principles

- One function, one clear responsibility.
- Names should explain intent, not implementation detail.
- Make invalid states hard to represent.
- Push side effects to boundaries.
- Prefer explicit errors with context over silent failure.

## Implementation Checklist

1. Clarify the contract: input, output, failure modes.
2. Keep units small and composable.
3. Replace magic constants with named values.
4. Remove duplicated branches and repeated literals.
5. Keep control flow shallow; return early on guard checks.
6. Add targeted tests for edge cases and failure paths.
7. Update docs if public behavior changes.

## Refactoring Pattern

1. Lock current behavior with tests.
2. Extract pure helpers from large functions.
3. Rename identifiers for domain clarity.
4. Introduce domain-specific exceptions where needed.
5. Re-run full quality gates.

## Quality Bar

- Public methods have type hints and deterministic return values.
- Exceptions include actionable context.
- No dead code or commented-out blocks.
- New complexity comes with tests.

## Anti-Patterns

- Generic names like `data`, `value`, `helper`, `util`.
- Catch-all `except Exception` without re-raising context.
- Mixed responsibilities in one function (I/O + transform + orchestration).
- Tests that only assert truthiness without business intent.
