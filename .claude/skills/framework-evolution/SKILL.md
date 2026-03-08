---
name: framework-evolution
description: Evolve automation framework architecture safely with backward compatibility, ADR documentation, and migration support.
---

# Framework Evolution

## Use This Skill When

- Designing shared automation framework components
- Evolving fixture, plugin, or config architecture
- Defining extension points and boundaries
- Making architecture-impacting changes

## Design Principles

- Separate concerns: config, driver, actions, reporting
- Keep framework APIs small and explicit
- Make extension hooks intentional and documented
- Prefer convention with escape hatches

## Decision Checklist

Before making architecture changes, answer:
1. Which layer owns this behavior?
2. How is backward compatibility preserved?
3. How will failure be observed and debugged?
4. How will this behave under parallel execution (xdist)?

## Evolution Procedure

1. Define current pain and measurable improvement
2. Propose architecture change and alternatives
3. Record decision in ADR (`docs/decisions/`)
4. Implement behind clear boundaries
5. Add migration notes for user-facing changes
6. Validate behavior in clean, retry, and xdist paths

## Rules

- Backward-compatible changes preferred over breaking
- Breaking changes require migration notes and deprecation window
- Every design-impacting choice gets an ADR
- Validate all execution modes: clean, clean-session, debug, xdist

## Definition of Done

- Decision documented in ADR
- Migration impact clear
- No regressions in core execution modes
