---
name: automation-framework-architecture
description: Framework design skill for fixtures, actions, page objects, config layering, diagnostics, and plugin architecture in test automation systems.
---

# Automation Framework Architecture

## Use This Skill When

- Designing shared automation framework components.
- Evolving fixture/plugin/config architecture.
- Defining extension points and boundaries.

## Architecture Guidelines

- Separate concerns: config, driver, actions, reporting.
- Keep framework APIs small and explicit.
- Make extension hooks intentional and documented.
- Prefer convention with escape hatches.

## Decision Checklist

1. Which layer owns this behavior?
2. How is backward compatibility preserved?
3. How will failure be observed and debugged?
4. How will this behave under parallel execution?

## Outputs

- ADR in `decisions/` for design-impacting changes.
- Migration notes when public behavior changes.
