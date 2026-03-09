---
name: refactor
description: Systematic code refactoring with behavioral preservation, safety nets, and incremental validation.
---

# Refactor

## Use This Skill When

- Restructuring modules or moving code between files
- Extracting classes or functions from large modules
- Simplifying complex control flow
- Reducing duplication across the codebase
- Splitting a large file into smaller focused modules

## Refactor Procedure

1. **Identify the target**: what specific code needs restructuring and why
2. **Baseline tests**: run `python3 -m pytest -q` and record passing count
3. **Map dependencies**: grep for all imports and usages of the target code
4. **Plan moves**: list exactly what moves where, what renames happen
5. **Execute incrementally**: one structural change at a time, test after each
6. **Update imports**: fix all import paths across the codebase
7. **Update exports**: if public API, update `__init__.py` to preserve the import path
8. **Verify baseline**: re-run full test suite, confirm same pass count
9. **Run lint**: `python3 -m ruff check .` to catch import issues

## Safety Checklist

- [ ] Full test suite passes before starting
- [ ] All callers of moved code identified (grep for class/function names)
- [ ] Public API preserved (same exports from `__init__.py`)
- [ ] No new public API surface introduced accidentally
- [ ] Internal imports updated (`_internal/` modules)
- [ ] Test imports updated (`tests/unit/`)
- [ ] Example imports updated (`examples/`)
- [ ] Full test suite passes after finishing
- [ ] Lint passes after finishing

## When Moving Code Between Modules

```
Before: src/appium_pytest_kit/big_module.py (ClassA, ClassB, helper_fn)
After:  src/appium_pytest_kit/module_a.py (ClassA)
        src/appium_pytest_kit/module_b.py (ClassB, helper_fn)
```

1. Create new files with the extracted code
2. Update `__init__.py` to import from new locations
3. Remove code from original file
4. Grep for direct imports of the original module and update them
5. Run tests

## Rules

- Never change behavior during a refactor — structural changes only
- One structural change per commit if the refactor is large
- If a refactor requires behavior changes, do them in a separate commit
- Preserve public API: if `from appium_pytest_kit import X` worked before, it must work after
- Internal modules (`_internal/`) can be freely restructured
- Don't refactor code you haven't read and understood
- Don't introduce abstractions for one-time operations

## Anti-Patterns

- Refactoring and adding features in the same change
- Moving code without updating all import sites
- Creating abstractions "for future use"
- Renaming things without grepping for all usages
- Breaking public import paths without deprecation

## Definition of Done

- Same test pass count before and after
- Lint passes
- Public API unchanged (or deprecated with migration notes)
- No dead imports or unused files
- Code is simpler or better organized than before
