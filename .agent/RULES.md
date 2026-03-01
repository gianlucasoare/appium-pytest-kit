# Operational Rules

Rules added from recurring patterns in recent implementation, CI, and release
cycles.

## 1) Release Preflight Is Mandatory

Before any PyPI push or release tag:

1. `python3 -m ruff check .`
2. `python3 -m pytest -q`
3. `python3 -m pytest -q -n 2 -m "not quarantine"` (xdist sanity lane)
4. `python3 -m build`
5. `python3 -m twine check dist/*`

If any step fails, release is blocked.

## 2) CI Failure Handling Must Be Evidence-First

- Start from the first real traceback, not the final summary line.
- Reproduce with the closest local lane command.
- Add/adjust a regression test for the discovered root cause.
- Re-run only the impacted lane first, then the full suite.

## 3) xdist-Safe Reporting Rules

- Never assume report files exist per worker.
- Use safe existence checks before reading worker artifacts.
- Treat controller and worker responsibilities separately in plugin hooks.
- File merge logic must be idempotent and resilient to missing partial files.

## 4) Security Rules For Tokens And Secrets

- Never store tokens in source files, docs, or issue comments.
- If a token is pasted in chat/logs, rotate it immediately and treat as exposed.
- Use environment variables for API/Auth/PyPI secrets.

## 5) Docs Must Ship With Behavior Changes

Any new fixture/helper/CLI behavior requires:

- update in `README.md` feature or usage section
- update or add a focused doc in `docs/`
- update scaffold docs when generated files change

## 6) Publish Verification Rules

After release workflow completes:

- verify version on PyPI
- verify GitHub release notes
- verify install path (`pip install appium-pytest-kit==X.Y.Z`) and import smoke
