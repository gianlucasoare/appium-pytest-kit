---
name: pr-prep
description: Prepare well-structured pull requests with change classification, testing plan, and reviewer context.
---

# PR Prep

## Use This Skill When

- About to open a pull request
- Reviewing a draft PR before requesting review
- Ensuring the PR satisfies the change protocol
- Writing PR descriptions for complex changes

## PR Preparation Procedure

1. **Classify the change** using the change protocol:
   - **Patch**: bug fix, no API or behavior change
   - **Minor**: backward-compatible new feature or setting
   - **Major**: breaking API change — requires deprecation window + migration notes
2. **Confirm version bump** in `pyproject.toml` matches the change class
3. **Write PR title**: `<type>(<scope>): <imperative short description>` (conventional commits)
   - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`
   - Example: `feat(waits): add for_count_at_least wait method`
4. **Write PR body** covering:
   - **What changed**: specific files and behaviors
   - **Why**: motivation — bug, user request, reliability, performance
   - **Test evidence**: which tests cover the change, new tests added
   - **Backward compat**: any public API additions/changes, migration notes if needed
   - **Checklist**: all preflight steps that passed
5. **Verify docs are updated**: every behavior change needs a doc update
6. **Check example projects**: do `examples/` still work with the changes?

## PR Title Format

```
feat(fixture-design): add page_factory fixture for deferred page instantiation
fix(diagnostics): skip video attachment when recording is disabled
refactor(server): extract port-isolation logic to _internal module
docs(waits): add for_count_at_least to waits.md
chore(deps): bump pydantic-settings to >=2.4.0
perf(actions): cache compiled locator strategies in Waiter
test(pytest-plugin): add regression for xdist session-mode isolation
```

## PR Body Template

```markdown
## What
[1-3 sentences describing the change]

## Why
[1-2 sentences on motivation]

## Change Classification
- [ ] Patch (bug fix, no API change)
- [ ] Minor (backward-compatible addition)
- [ ] Major (breaking change — migration notes included)

## Test Evidence
- Added: `tests/unit/test_<module>.py::<test_name>`
- Existing: all unit tests pass

## Docs Updated
- [ ] `docs/<relevant-file>.md`
- [ ] `README.md` (if public API surface changed)

## Preflight
- [ ] `python3 -m ruff check .`
- [ ] `python3 -m pytest -q`
- [ ] `python3 -m pytest -q -n 2 -m "not quarantine"`
```

## Rules

- Never open a PR with failing tests or lint errors
- Always classify patch/minor/major before setting the version bump
- Major changes require a migration section in the PR body
- Link related issues with `Closes #N` or `Fixes #N`
- Prefer small, focused PRs over large omnibus changes
- Quarantine or remove tests that would flake in CI before opening

## Definition of Done

- Title follows conventional commits format
- Change correctly classified (patch/minor/major)
- Version bump in `pyproject.toml` matches classification
- PR body covers what, why, test evidence, and docs
- All preflight steps passed locally
