# Device Farm Cloud Providers

Run your tests on BrowserStack, Sauce Labs, or AWS Device Farm with zero capability boilerplate. The `cloud` module handles authentication, server URLs, and vendor-specific capability namespacing.

---

## Quick start

```python
# conftest.py
from appium_pytest_kit.cloud import build_cloud_config, apply_cloud_config

def pytest_appium_pytest_kit_capabilities(capabilities, settings):
    """Inject cloud capabilities when APP_CLOUD_PROVIDER is set."""
    import os
    provider = os.environ.get("APP_CLOUD_PROVIDER")
    if not provider:
        return None

    cloud = build_cloud_config(
        provider,
        project="My App",
        build=os.environ.get("CI_BUILD_ID", "local"),
        device=settings.device_name,
    )
    return apply_cloud_config(capabilities, cloud)
```

```bash
# Run on BrowserStack
export APP_CLOUD_PROVIDER=browserstack
export BROWSERSTACK_USERNAME=your_user
export BROWSERSTACK_ACCESS_KEY=your_key
export BROWSERSTACK_APP=bs://abc123
pytest tests/
```

---

## Supported providers

### BrowserStack

**Required env vars:**

| Variable | Description |
|---|---|
| `BROWSERSTACK_USERNAME` | BrowserStack account username |
| `BROWSERSTACK_ACCESS_KEY` | BrowserStack access key |

**Optional env vars:**

| Variable | Description |
|---|---|
| `BROWSERSTACK_APP` | Uploaded app URL (e.g. `bs://abc123`) |

**Python API:**

```python
from appium_pytest_kit.cloud import build_cloud_config

config = build_cloud_config(
    "browserstack",
    project="MyApp",          # bstack:options.projectName
    build="CI #42",           # bstack:options.buildName
    name="Login Test",        # bstack:options.sessionName
    device="Google Pixel 7",  # bstack:options.deviceName
    os_version="13.0",        # bstack:options.osVersion
    app="bs://abc123",        # bstack:options.appUrl (overrides env)
    extra={                   # any additional capabilities
        "appium:autoGrantPermissions": True,
    },
)

# config.server_url  → https://user:key@hub-cloud.browserstack.com/wd/hub
# config.capabilities → {"bstack:options": {...}}
```

---

### Sauce Labs

**Required env vars:**

| Variable | Description |
|---|---|
| `SAUCE_USERNAME` | Sauce Labs username |
| `SAUCE_ACCESS_KEY` | Sauce Labs access key |

**Optional env vars:**

| Variable | Description |
|---|---|
| `SAUCE_APP` | Storage ID (e.g. `storage:filename=app.apk`) |

**Python API:**

```python
from appium_pytest_kit.cloud import build_cloud_config

config = build_cloud_config(
    "saucelabs",
    device="iPhone 14",
    platform_version="16.0",
    data_center="eu-central-1",   # default: us-west-1
    build="CI #42",               # sauce:options.build
    name="Smoke Suite",           # sauce:options.name
    app="storage:filename=my.ipa",
)

# config.server_url  → https://user:key@ondemand.eu-central-1.saucelabs.com:443/wd/hub
# config.capabilities → {"sauce:options": {...}, "appium:deviceName": "iPhone 14", ...}
```

---

### AWS Device Farm

**Required env vars:**

| Variable | Description |
|---|---|
| `AWS_DEVICE_FARM_ARN` | Project ARN (or pass `project_arn` argument) |
| `AWS_DEFAULT_REGION` | AWS region (default: `us-west-2`) |

Standard AWS credential env vars (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) must also be set.

**Python API:**

```python
from appium_pytest_kit.cloud import build_cloud_config

config = build_cloud_config(
    "aws",
    project_arn="arn:aws:devicefarm:us-west-2:123456:project:abc",
)

# config.server_url  → https://devicefarm.us-west-2.amazonaws.com
# config.capabilities → {"appium:deviceFarm:projectArn": "arn:..."}
```

---

## Using with `build_driver_config`

The `CloudConfig` integrates with the existing driver configuration pipeline:

```python
from appium_pytest_kit import build_driver_config, create_driver, load_settings
from appium_pytest_kit.cloud import build_cloud_config, apply_cloud_config

settings = load_settings()
cloud = build_cloud_config("browserstack", project="MyApp", build="CI #1")

# Build config with cloud server URL
driver_config = build_driver_config(settings, server_url=cloud.server_url)

# Merge cloud capabilities
merged_caps = apply_cloud_config(driver_config.capabilities, cloud)
```

---

## Using with hooks (recommended)

The cleanest integration is through the capabilities hook:

```python
# conftest.py
import os
from appium_pytest_kit.cloud import build_cloud_config, apply_cloud_config

def pytest_appium_pytest_kit_capabilities(capabilities, settings):
    provider = os.environ.get("APP_CLOUD_PROVIDER")
    if not provider:
        return None

    cloud = build_cloud_config(
        provider,
        project="My App",
        build=os.environ.get("CI_BUILD_ID", "local"),
        name=os.environ.get("PYTEST_CURRENT_TEST", "unknown"),
        device=settings.device_name,
        os_version=settings.platform_version,
    )
    return apply_cloud_config(capabilities, cloud)
```

This approach:

- Does nothing when running locally (no `APP_CLOUD_PROVIDER` set)
- Automatically adapts when CI sets the provider and credentials
- Keeps cloud config out of your test code

---

## CI configuration examples

### GitHub Actions + BrowserStack

```yaml
jobs:
  test-cloud:
    runs-on: ubuntu-latest
    env:
      APP_CLOUD_PROVIDER: browserstack
      BROWSERSTACK_USERNAME: ${{ secrets.BROWSERSTACK_USERNAME }}
      BROWSERSTACK_ACCESS_KEY: ${{ secrets.BROWSERSTACK_ACCESS_KEY }}
      BROWSERSTACK_APP: ${{ secrets.BROWSERSTACK_APP }}
      APP_DEVICE_NAME: "Google Pixel 7"
      APP_PLATFORM_VERSION: "13.0"
    steps:
      - uses: actions/checkout@v4
      - run: pip install appium-pytest-kit
      - run: pytest tests/ -v
```

### GitHub Actions + Sauce Labs

```yaml
jobs:
  test-cloud:
    runs-on: ubuntu-latest
    env:
      APP_CLOUD_PROVIDER: saucelabs
      SAUCE_USERNAME: ${{ secrets.SAUCE_USERNAME }}
      SAUCE_ACCESS_KEY: ${{ secrets.SAUCE_ACCESS_KEY }}
      SAUCE_APP: ${{ secrets.SAUCE_APP }}
    steps:
      - uses: actions/checkout@v4
      - run: pip install appium-pytest-kit
      - run: pytest tests/ -v
```

---

## Error handling

Missing credentials raise `ConfigurationError` with a clear message:

```
appium_pytest_kit.errors.ConfigurationError: BrowserStack requires environment variable
BROWSERSTACK_USERNAME. Set it via export or CI secrets.
```

Unknown provider names also raise `ConfigurationError`:

```
appium_pytest_kit.errors.ConfigurationError: Unknown cloud provider 'unknown'.
Supported: aws, browserstack, saucelabs
```

---

## Importing

```python
from appium_pytest_kit import (
    CloudConfig,          # config dataclass
    build_cloud_config,   # factory function
    apply_cloud_config,   # capability merger
)
```
