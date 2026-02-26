# Installation

## System requirements

| Requirement | Minimum version | Notes |
|---|---|---|
| Python | 3.11 | 3.12 and 3.13 also supported |
| Node.js | 18 | Required to run the Appium server |
| Appium | 2.x | `npm install -g appium` |
| Android SDK | — | Required for Android testing (`adb` must be on PATH) |
| Xcode | 14+ | Required for iOS testing (macOS only) |

---

## Step 1 — Install Appium and a platform driver

```bash
# Install Appium globally
npm install -g appium

# Android driver (UiAutomator2)
appium driver install uiautomator2

# iOS driver (XCUITest) — macOS only
appium driver install xcuitest

# Verify everything is installed
appium driver list --installed
```

Start Appium to confirm it works:

```bash
appium
# Appium HTTP listening on http://0.0.0.0:4723
```

---

## Step 2 — Create a Python virtual environment

Always use a virtual environment to keep your project dependencies isolated:

```bash
python -m venv .venv

# Activate (macOS / Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

---

## Step 3 — Install appium-pytest-kit

### From PyPI (recommended)

```bash
pip install appium-pytest-kit
```

### From GitHub (latest main branch)

```bash
pip install git+https://github.com/gianlucasoare/appium-pytest-kit.git
```

### Specific branch or tag

```bash
pip install git+https://github.com/gianlucasoare/appium-pytest-kit.git@main
pip install git+https://github.com/gianlucasoare/appium-pytest-kit.git@v0.1.1
```

### Local clone (for development or contributing)

```bash
git clone https://github.com/gianlucasoare/appium-pytest-kit.git
cd appium-pytest-kit
pip install -e ".[dev]"
```

---

## What gets installed automatically

`pip install appium-pytest-kit` automatically installs **all required dependencies**. You do not need a separate `requirements.txt`.

| Package | Version | Purpose |
|---|---|---|
| `Appium-Python-Client` | ≥ 4.0.0 | Appium WebDriver client |
| `pydantic-settings` | ≥ 2.3.0 | Settings loading from `.env` and env vars |
| `pytest` | ≥ 8.2.0 | Test runner the plugin integrates with |

---

## Optional extras

Some features require additional packages. Install them with pip extras:

```bash
# Device profile YAML support (data/devices.yaml)
pip install "appium-pytest-kit[yaml]"

# Allure report attachments (screenshots + page source in Allure)
pip install "appium-pytest-kit[allure]"

# Retry failed tests with session reuse
pip install "appium-pytest-kit[retry]"

# Parallel workers with pytest-xdist
pip install "appium-pytest-kit[xdist]"

# All optional extras at once
pip install "appium-pytest-kit[all]"
```

| Extra | Package | When you need it |
|---|---|---|
| `[yaml]` | `PyYAML >= 6.0` | Using named device profiles in `data/devices.yaml` |
| `[allure]` | `allure-pytest >= 2.13.0` | Attaching artifacts to Allure reports |
| `[retry]` | `pytest-retry >= 0.6.0` | Retrying flaky tests while reusing driver sessions |
| `[xdist]` | `pytest-xdist >= 3.6.0` | Parallel test execution (`pytest -n N`) |
| `[all]` | All optional extras above | Install everything in one command |

> **Note:** If you don't install `[yaml]`, device profile loading will raise a `ConfigurationError` with a clear message telling you to install PyYAML. If you don't install `[allure]`, Allure attachment is silently skipped — no error.

---

## Verify the installation

```bash
# Check the CLI tool is available
appium-pytest-kit-init --help
appium-pytest-kit-doctor --help

# Check the package version
python -c "import appium_pytest_kit; print(appium_pytest_kit.__version__)"

# Confirm the pytest plugin is registered
pytest --co -q  # should not error even with no test files
```

---

## Maintainer release flow

This repo ships `.github/workflows/release.yml` for Trusted Publishing to PyPI.
Create and push a version tag (for example `v0.1.8`) to run tests, build artifacts,
verify `vX.Y.Z` matches `project.version`, and publish automatically.

The `publish` job is tag-guarded, so manual workflow runs from branches do not
upload to PyPI.

For release notes, run `.github/workflows/changelog.yml` (manual dispatch) to
generate a `CHANGELOG.md` section and open a PR.

---

## Next steps

- [Project structure →](project-structure.md) — set up your test project
- [Configuration →](configuration.md) — configure your device and app
