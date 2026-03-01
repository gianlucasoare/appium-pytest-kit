---
name: python-craft
description: Python engineering skill focused on readability, typing, error handling, maintainability, and testability in production automation code.
---

# Python Craft

## Use This Skill When

- Writing or reviewing Python modules.
- Improving code quality and maintainability.
- Adding scripts used in CI/release workflows.

## Standards

- Favor small pure helpers for complex logic.
- Add type hints for non-trivial interfaces.
- Raise domain-specific errors with useful context.
- Keep side effects explicit at boundaries.

## Checklist

1. Input validation and safe defaults.
2. Structured logging for critical operations.
3. Unit tests for edge cases and error paths.
4. Lint/format/type compatibility.

## Common Mistakes To Avoid

- Catch-all exceptions without context.
- Hidden mutable globals.
- Overloaded functions with mixed concerns.
