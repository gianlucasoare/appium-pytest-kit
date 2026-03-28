---
description: Rules for documentation files
globs:
  - "docs/**"
  - "README.md"
  - "DOCUMENTATION.md"
---

# Documentation Rules

## Structure
- Every public module in `src/appium_pytest_kit/` must have a corresponding doc page in `docs/`
- Every doc page must be listed in `mkdocs.yml` nav — orphan pages break the hosted site
- Doc file names use kebab-case: `soft-assertions.md`, `cloud-providers.md`
- Use sections: intro paragraph, quick start, API reference, real-world patterns, importing

## Code Examples
- All code examples must use the current public API from `__init__.py` — never reference internal modules directly
- Import examples must be copy-pasteable: include the full `from appium_pytest_kit import ...` line
- Use realistic locators and variable names, not `foo`/`bar`/`test123`
- Show error handling patterns where the user is likely to hit exceptions

## Cross-Referencing
- Link to related docs with relative paths: `[errors reference](errors.md)`
- Every error class mentioned must link to its section in `docs/errors.md`
- Every setting mentioned must use the `APP_` env var name and link to `docs/configuration.md`
- Every fixture mentioned must link to `docs/fixtures.md`

## Tables
- API reference tables must include: parameter name, type, default (if any), description
- Error context tables must include: attribute name, type, description
- Keep tables under 6 columns — wider tables break on mobile

## README.md Specifics
- Feature table in "What it gives you" must stay in sync with actual features
- Public API import block must match `__init__.py` `__all__` exactly
- Docs index table must list every doc page with a working relative link
- Optional extras table must match `pyproject.toml` `[project.optional-dependencies]`

## Sync Requirements
- When a public class/function is added: update `docs/errors.md` hierarchy if error, add doc page, update `docs/index.md` next steps, update README feature table and public API block
- When a setting is added: update `docs/configuration.md`
- When a CLI flag is added: update `docs/cli-reference.md`
- Run `mkdocs build --strict` to verify — warnings about missing pages are build-breaking
