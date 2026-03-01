# Agent Operating System

This folder is the local operating system for engineering work in this repository.

Quick navigation: see [`INDEX.md`](INDEX.md).

## Goals

- Keep decisions explicit and auditable.
- Reuse reliable workflows instead of improvising.
- Raise quality through repeatable test and release gates.

## Structure

- `skills/`: domain skills with `SKILL.md` instructions.
- `workflows/`: task execution runbooks.
- `decisions/`: architecture decision records (ADR).
- `templates/`: reusable document/checklist templates.
- `playbooks/`: incident and improvement playbooks.
- `backlog/`: suggested future capabilities.
- Root docs: `commands.md`, `OWNERS.md`, `RISK_REGISTER.md`, `METRICS.md`,
  `CHANGE_PROTOCOL.md`, `SECURITY_BASELINE.md`, `RULES.md`, `ROADMAP.md`.

## How To Use

1. Pick the closest workflow from `workflows/`.
2. Apply one or more relevant skills from `skills/`.
3. Capture key choices in `decisions/` when design-impacting.
4. Use templates for consistency.
5. Record improvements in `backlog/`.

## Core Principles

- Prefer deterministic automation over ad-hoc steps.
- Keep tests isolated, observable, and diagnosable.
- Enforce quality gates in CI before release.
- Document tradeoffs, not just conclusions.
