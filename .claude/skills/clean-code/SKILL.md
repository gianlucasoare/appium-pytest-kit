---
name: clean-code
description: Write and refactor clean, maintainable Python code with clear naming, small units, explicit error handling, and test-backed behavior.
---

# Clean Code

## Use This Skill When

- Implementing new modules or APIs
- Refactoring legacy code without changing behavior
- Reviewing PRs for readability and maintainability
- Writing or reviewing Python scripts for CI/release

## Core Principles

- One function, one clear responsibility
- Names should explain intent, not implementation detail
- Make invalid states hard to represent
- Push side effects to boundaries
- Prefer explicit errors with context over silent failure
- Favor small pure helpers for complex logic

## Implementation Checklist

1. Clarify the contract: input, output, failure modes
2. Keep units small and composable
3. Replace magic constants with named values
4. Remove duplicated branches and repeated literals
5. Keep control flow shallow; return early on guard checks
6. Add type hints for non-trivial interfaces
7. Add input validation and safe defaults
8. Use structured logging for critical operations
9. Add targeted tests for edge cases and failure paths
10. Verify lint, format, and type compatibility

## Refactoring Pattern

1. Add characterization tests that lock current behavior
2. Extract small, named helpers for complex logic
3. Simplify control flow and remove dead branches
4. Rename for clarity where intent is obscured
5. Run full suite to confirm behavior is preserved

## Quality Bar

- Public methods have type hints and deterministic return values
- Exceptions include actionable context (never bare `raise`)
- No dead code or commented-out blocks
- New complexity comes with tests

## Anti-Patterns

- Generic names (`data`, `result`, `temp`, `helper`)
- Catch-all exceptions without context
- Mixed responsibilities in a single function
- Tests without business intent
- Hidden mutable globals
- Overloaded functions with mixed concerns
