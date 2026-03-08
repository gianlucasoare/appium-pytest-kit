---
name: ai-assisted-engineering
description: Use AI effectively in engineering work with decomposition, verification loops, risk control, and output validation.
---

# AI-Assisted Engineering

## Use This Skill When

- Planning medium or large implementation tasks
- Generating drafts that must be productionized
- Reviewing risk and validating generated outputs

## Execution Pattern

1. Decompose into verifiable increments
2. Implement the smallest useful slice
3. Run checks after each slice (lint, test, type check)
4. Capture assumptions and unresolved risks
5. Finalize with concise change summary

## Guardrails

- Never trust generated code without tests
- Validate external assumptions against source files
- Prefer reproducible scripts over manual procedures
- Keep generated code consistent with existing project style
