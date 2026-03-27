# appium-pytest-kit

Reusable Appium 2.x + pytest plugin library for Python 3.11+. Install it once, generate a `.env`, and start writing mobile tests with zero boilerplate.

```bash
pip install appium-pytest-kit
appium-pytest-kit-init --framework --root my-project
```

## What it gives you

| | |
|---|---|
| **Zero-config fixtures** | `driver`, `waiter`, `actions`, `page_factory` — just add to your test function |
| **Auto failure artifacts** | Screenshot + page source + device logs + session log captured automatically on failure |
| **3-tier device resolution** | explicit settings → named profile → auto-detect via adb/xcrun |
| **Session modes** | `clean` (per-test) · `clean-session` (shared) · `debug` (keep alive) |
| **Retry support** | Session reused across retry attempts — no restart cost between tries |
| **xdist parallelism** | Worker-safe capability port isolation + per-worker managed Appium ports |
| **Explicit waits** | `WaitTimeoutError` with structured `.locator` and `.timeout` context |
| **High-level actions** | tap, type, swipe, scroll, assertions — all wait-safe |
| **API testing** | Lightweight `ApiClient` for backend assertions in the same pytest run |
| **Page + flow objects** | Scaffold generates `pages/` and `flows/` with base classes ready to extend |
| **Extension hooks** | Override settings, inject capabilities, run code after driver creation |
| **CLI scaffold** | One command to generate a full project structure |

## Quick start

```bash
# 1. Install
pip install appium-pytest-kit

# 2. Scaffold a project
appium-pytest-kit-init --framework --root my-app

# 3. Configure
cd my-app
cp .env.example .env
# edit .env with your device/app details

# 4. Run
pytest
```

## Next steps

- [Installation](installation.md) — system requirements and setup
- [Configuration](configuration.md) — all settings reference
- [Fixtures](fixtures.md) — built-in fixtures and lifecycle
- [Actions Reference](actions.md) — 50+ high-level UI actions
- [Waits Reference](waits.md) — explicit wait primitives
