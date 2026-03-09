---
name: appium-kit-delivery
description: Plan and ship framework changes in appium-pytest-kit. Use when adding or changing fixtures, helpers, settings, hooks, CLI behavior, scaffold output, internal modules, examples, or architecture boundaries, especially when tests, docs, changelog entries, or ADR follow-through must stay aligned.
---

# Appium Kit Delivery

Implement framework work in small, verifiable slices. Use live source files as the source of truth instead of copying API details into the plan.

## Workflow

1. Read the closest existing implementation before changing structure or naming.
2. Classify the change surface: public API, internal module, fixture, hook, settings, CLI, scaffold, docs, or examples.
3. Confirm whether the work is patch, minor, or major according to the repo guidance in `AGENTS.md`.
4. Add or adjust tests first when the desired behavior is already clear.
5. Implement the smallest useful slice and validate it before widening scope.
6. Update docs, examples, changelog notes, or ADRs in the same change set when the surface is user-facing or architectural.

## Repo-Specific Checks

- If the change touches scaffold output in `src/appium_pytest_kit/cli.py`, update `docs/project-structure.md` and `docs/cli-reference.md`.
- If the change introduces or changes a public fixture, helper, hook, or settings field, update the matching docs and `README.md`.
- If the change alters architecture or extension boundaries, add or update an ADR in `docs/decisions/`.
- If the change could affect release semantics, also read `$appium-kit-release`.

## Delivery Rules

- Preserve public contracts unless the work explicitly includes migration notes and version follow-through.
- Reuse existing patterns from `pytest_plugin.py`, `settings.py`, `cli.py`, and `_internal/` modules instead of inventing a new style.
- Keep implementation and cleanup in the same patch. Do not leave docs or examples stale for a later step.
- Prefer targeted commands first, then broader validation once the slice is stable.

## Done

- Behavior is implemented at the correct boundary.
- Tests cover the new and unchanged behavior.
- Docs and examples match the final code.
- Release impact is understood.
