# appium-pytest-kit

This file applies to the entire repository unless a deeper `AGENTS.md` overrides it.

## Repository Identity

- PyPI package: `appium-pytest-kit`
- Import path: `appium_pytest_kit`
- Source layout: `src/appium_pytest_kit/`
- Python: `>=3.11`
- CLI entry points: `appium-pytest-kit-init`, `appium-pytest-kit-doctor`
- pytest11 entry point: `appium-pytest-kit = "appium_pytest_kit.pytest_plugin"`

## Working Commands

- Install dev dependencies: `python3 -m pip install -e ".[dev]"`
- Lint: `python3 -m ruff check .`
- Unit tests: `python3 -m pytest -q`
- Example collection: `python3 -m pytest --collect-only examples/basic/tests -q`

## CI Lanes

- Main lane: `python3 -m pytest -q -m "not quarantine"`
- Quarantine lane: `python3 -m pytest -q -m quarantine`
- xdist sanity lane: `python3 -m pytest -q -n 2 -m "not quarantine"`

## Release Preflight

Before any PyPI publish or release tag, all of these must pass:

1. `python3 -m ruff check .`
2. `python3 -m pytest -q`
3. `python3 -m pytest -q -n 2 -m "not quarantine"`
4. `python3 -m build`
5. `python3 -m twine check dist/*`

After release, verify the published PyPI version, GitHub release notes, and an install smoke test.

## Architecture Notes

- Treat `src/appium_pytest_kit/_internal/` as non-public implementation detail.
- **Public modules**: `actions.py`, `api.py`, `cloud.py`, `driver.py`, `errors.py`, `hooks.py`, `interfaces.py`, `locator_healing.py`, `parametrize.py`, `settings.py`, `soft_assertions.py`, `test_data.py`, `visual.py`, `waits.py`
- Prefer safe `pytest.Config.stash` access and typed stash keys over globals.
- `AppiumPytestKitSettings` is the primary settings surface and uses the `APP_` env prefix.
- Hook specs live in `AppiumPytestKitHookSpecs`.
- **Error hierarchy**: `AppiumPytestKitError` → `ConfigurationError`, `DeviceResolutionError`, `LaunchValidationError`, `WaitTimeoutError`, `ActionError`, `DriverCreationError`, `ApiRequestError`, `VisualRegressionError`, `SoftAssertionError`
- **Cloud providers**: `build_cloud_config()` for BrowserStack, Sauce Labs, AWS Device Farm with env-var auth
- **Locator healing**: `LocatorChain`, `HealingRegistry`, `chain()` shorthand for fallback locator strategies
- **Soft assertions**: `SoftAssert` with 10 check methods + `soft_assertions()` context manager
- **Test data**: `DataFactory` with seedable randomness, standalone generators for emails, phones, passwords
- Public behavior changes often touch docs under `docs/` and examples under `examples/`.

## Coding Conventions

- Do not use `from __future__ import annotations`; keep the existing exception only where the codebase already does.
- Import `Mapping`, `Iterable`, and `Sequence` from `collections.abc`, not `typing`.
- Use `wrapper=True` for `pytest_runtest_makereport`.
- Raise domain-specific errors with actionable context instead of generic exceptions. Errors carry structured attributes: `.locator`, `.timeout`, `.action`, `.failures`, `.method`, `.url`, `.status_code`, `.diff_ratio`, `.threshold` as appropriate.
- Keep public interfaces typed and deterministic.
- Keep Allure integration as a soft import, never a hard dependency.

## Change Protocol

- Classify changes as patch, minor, or major before release work.
- Preserve backward compatibility for public APIs unless a deliberate breaking change includes migration notes and versioning follow-through.
- Ship tests that prove both the new behavior and unchanged behavior.
- Ship docs with behavior. Update `README.md` and the relevant `docs/` files when public behavior changes.
- Add an ADR in `docs/decisions/` for architecture-impacting changes.
- If scaffold output changes, update `docs/project-structure.md` and `docs/cli-reference.md` in the same change.

## Operational Rules

- Start CI and debugging work from the first real traceback, not the summary line.
- Keep xdist paths safe: tolerate missing worker artifacts, separate controller and worker responsibilities, and make merge logic idempotent.
- Never store real tokens or secrets in source, docs, issues, or workflow files.
- Use environment variables or repository secrets for sensitive values.
- When current external documentation matters, use the existing Context7 capability instead of creating local copies of vendor docs.

## Local Codex Skills

- Read `.codex/skills/appium-kit-delivery/SKILL.md` when implementing or planning framework changes, new helpers, settings, hooks, CLI behavior, scaffold output, or architecture work.
- Read `.codex/skills/appium-kit-testing/SKILL.md` when designing tests, fixtures, retry-aware setup, xdist-safe lifecycle handling, or automation quality improvements.
- Read `.codex/skills/appium-kit-debug/SKILL.md` when triaging a failing or flaky test, CI lane, xdist issue, or intermittent workflow.
- Read `.codex/skills/appium-kit-doc-sync/SKILL.md` when docs, examples, README, or API references may be stale after a code change.
- Read `.codex/skills/appium-kit-release/SKILL.md` when preparing a version bump, compatibility review, changelog update, quality-gate change, or release plan.
- Read `.codex/skills/appium-kit-code-reviewer/SKILL.md` when the user asks for a review or you need severity-ordered findings.
- Read `.codex/skills/appium-kit-coverage-analyzer/SKILL.md` when mapping source modules to tests or prioritizing coverage gaps.
- Read `.codex/skills/appium-kit-debugger/SKILL.md` when actively reproducing and fixing a concrete failure.
- Read `.codex/skills/appium-kit-test-runner/SKILL.md` when executing lint or pytest lanes and reporting results.
- Read `.codex/skills/appium-kit-dependency-auditor/SKILL.md` when auditing, adding, removing, or changing dependencies and extras.
- Read `.codex/skills/appium-kit-doc-checker/SKILL.md` when comparing code surfaces against docs for missing, stale, or incomplete documentation.
- Read `.codex/skills/appium-kit-release-validator/SKILL.md` when running the mandatory release preflight and deciding whether release is blocked.

## Source Material

- `.claude/` is source material for Codex guidance. Do not modify `.claude/` as part of Codex-specific guidance work unless the user explicitly asks for it.

## Guidance Sync Policy

- `AGENTS.md` and `CLAUDE.md` should stay semantically aligned on repo-wide policy, commands, release gates, and architectural constraints.
- Update both root guidance files when a shared rule changes, even if only one assistant currently needs the change.
- Keep assistant-specific discovery details separate: Codex skill routing belongs in `AGENTS.md`, while Claude-specific routing belongs in `CLAUDE.md` or `.claude/`.
- If the two systems ever disagree, treat that as maintenance drift and reconcile the rule before relying on it.
