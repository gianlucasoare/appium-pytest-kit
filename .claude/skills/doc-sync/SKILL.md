---
name: doc-sync
description: Verify and enforce documentation-code alignment across fixtures, hooks, settings, errors, and CLI behavior.
---

# Doc Sync

## Use This Skill When

- A feature was added or changed and docs may be stale
- Reviewing whether documentation covers all public API
- Preparing a release and need to verify doc completeness
- A user reports confusing or outdated documentation

## Audit Procedure

1. **Inventory public API**: read `src/appium_pytest_kit/__init__.py` for all exports
2. **Cross-reference docs**: check each export against `docs/` files:
   - Fixtures → `docs/fixtures.md`
   - Settings fields → `docs/configuration.md`
   - Waiter methods → `docs/waits.md`
   - MobileActions methods → `docs/actions.md`
   - Error types → `docs/errors.md`
   - Hooks → `docs/conftest-guide.md`
   - CLI options → `docs/cli-reference.md`
   - Device resolution → `docs/device-resolution.md`
   - Session modes → `docs/session-modes.md`
   - API client → `docs/api-testing.md`
   - Page objects → `docs/page-objects.md`
3. **Check README.md**: verify quick-start examples still work with current API
4. **Check examples/**: verify example code uses current API (no deprecated patterns)
5. **Report gaps**: list undocumented or stale entries
6. **Fix gaps**: update docs to match current code behavior

## Coverage Checklist

- [ ] Every `AppiumPytestKitSettings` field documented with type, default, and env var name
- [ ] Every fixture documented with scope, type, and usage example
- [ ] Every hook documented with signature, return type, and conftest example
- [ ] Every error type documented with context attributes
- [ ] Every `Waiter` method documented with parameters and example
- [ ] Every `MobileActions` method documented with parameters and example
- [ ] CLI `--framework` scaffold output matches `docs/project-structure.md`
- [ ] `docs/troubleshooting.md` covers errors users actually hit

## Rules

- Docs ship with behavior — never merge a feature without its doc update
- Use the actual class/function names from code, not paraphrases
- Include code examples that can be copy-pasted
- Settings docs must show the `APP_` env var name, Python field name, type, and default
- Keep docs concise — reference the source for implementation details

## Definition of Done

- Every public export has a corresponding doc entry
- Examples compile against current API
- README quick-start is accurate
- No stale references to removed or renamed features
