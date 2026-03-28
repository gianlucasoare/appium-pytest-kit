"""Device farm cloud provider adapters for BrowserStack, Sauce Labs, and AWS Device Farm."""


import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from appium_pytest_kit.errors import ConfigurationError

logger = logging.getLogger(__name__)

CloudProvider = Literal["browserstack", "saucelabs", "aws"]


@dataclass(frozen=True, slots=True)
class CloudConfig:
    """Resolved cloud provider configuration.

    Attributes:
        provider: Provider name (``browserstack``, ``saucelabs``, ``aws``).
        server_url: Full Appium hub URL including credentials.
        capabilities: Extra capabilities injected by the adapter.
    """

    provider: CloudProvider
    server_url: str
    capabilities: dict[str, Any]


def _require_env(name: str, *, label: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        msg = (
            f"{label} requires environment variable {name}. "
            f"Set it via export or CI secrets."
        )
        raise ConfigurationError(msg)
    return value


# ── BrowserStack ─────────────────────────────────────────────────────────


def _browserstack_config(
    *,
    app: str | None = None,
    project: str | None = None,
    build: str | None = None,
    name: str | None = None,
    device: str | None = None,
    os_version: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> CloudConfig:
    """Build a BrowserStack cloud config from environment variables.

    Required env vars:
        ``BROWSERSTACK_USERNAME``, ``BROWSERSTACK_ACCESS_KEY``

    Optional env vars:
        ``BROWSERSTACK_APP`` (uploaded app URL like ``bs://…``)
    """
    username = _require_env("BROWSERSTACK_USERNAME", label="BrowserStack")
    access_key = _require_env("BROWSERSTACK_ACCESS_KEY", label="BrowserStack")

    server_url = f"https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub"

    bstack_options: dict[str, Any] = {}
    if project:
        bstack_options["projectName"] = project
    if build:
        bstack_options["buildName"] = build
    if name:
        bstack_options["sessionName"] = name
    if device:
        bstack_options["deviceName"] = device
    if os_version:
        bstack_options["osVersion"] = os_version

    resolved_app = app or os.environ.get("BROWSERSTACK_APP", "").strip()
    if resolved_app:
        bstack_options["appUrl"] = resolved_app

    caps: dict[str, Any] = {"bstack:options": bstack_options}
    if extra:
        caps.update(extra)

    logger.info("cloud:browserstack  server=%s  device=%s", server_url.split("@")[1], device)
    return CloudConfig(provider="browserstack", server_url=server_url, capabilities=caps)


# ── Sauce Labs ───────────────────────────────────────────────────────────


def _saucelabs_config(
    *,
    app: str | None = None,
    app_id: str | None = None,
    device: str | None = None,
    platform_version: str | None = None,
    data_center: str = "us-west-1",
    build: str | None = None,
    name: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> CloudConfig:
    """Build a Sauce Labs cloud config from environment variables.

    Required env vars:
        ``SAUCE_USERNAME``, ``SAUCE_ACCESS_KEY``

    Optional env vars:
        ``SAUCE_APP`` (storage ID like ``storage:filename=app.apk``)
    """
    username = _require_env("SAUCE_USERNAME", label="Sauce Labs")
    access_key = _require_env("SAUCE_ACCESS_KEY", label="Sauce Labs")

    server_url = f"https://{username}:{access_key}@ondemand.{data_center}.saucelabs.com:443/wd/hub"

    sauce_options: dict[str, Any] = {}
    if build:
        sauce_options["build"] = build
    if name:
        sauce_options["name"] = name

    resolved_app = app or app_id or os.environ.get("SAUCE_APP", "").strip()
    if resolved_app:
        sauce_options["app"] = resolved_app

    caps: dict[str, Any] = {"sauce:options": sauce_options}
    if device:
        caps["appium:deviceName"] = device
    if platform_version:
        caps["appium:platformVersion"] = platform_version
    if extra:
        caps.update(extra)

    logger.info("cloud:saucelabs  data_center=%s  device=%s", data_center, device)
    return CloudConfig(provider="saucelabs", server_url=server_url, capabilities=caps)


# ── AWS Device Farm ──────────────────────────────────────────────────────


def _aws_config(
    *,
    project_arn: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> CloudConfig:
    """Build an AWS Device Farm cloud config from environment variables.

    Required env vars:
        ``AWS_DEVICE_FARM_ARN`` (or pass ``project_arn`` argument)

    AWS credentials are expected via standard env vars:
        ``AWS_ACCESS_KEY_ID``, ``AWS_SECRET_ACCESS_KEY``, ``AWS_SESSION_TOKEN``
    """
    arn = project_arn or os.environ.get("AWS_DEVICE_FARM_ARN", "").strip()
    if not arn:
        msg = (
            "AWS Device Farm requires AWS_DEVICE_FARM_ARN environment variable "
            "or project_arn argument."
        )
        raise ConfigurationError(msg)

    region = os.environ.get("AWS_DEFAULT_REGION", "us-west-2")
    server_url = f"https://devicefarm.{region}.amazonaws.com"

    caps: dict[str, Any] = {
        "appium:deviceFarm:projectArn": arn,
    }
    if extra:
        caps.update(extra)

    logger.info("cloud:aws_device_farm  arn=%s", arn)
    return CloudConfig(provider="aws", server_url=server_url, capabilities=caps)


# ── Public factory ───────────────────────────────────────────────────────


def build_cloud_config(
    provider: str,
    **kwargs: Any,
) -> CloudConfig:
    """Build a cloud config for the specified provider.

    Args:
        provider: One of ``browserstack``, ``saucelabs``, ``aws``.
        **kwargs: Provider-specific arguments (see individual functions).

    Returns:
        A ``CloudConfig`` with the resolved server URL and capabilities.

    Raises:
        ConfigurationError: If required credentials are missing or provider is unknown.

    Example::

        from appium_pytest_kit.cloud import build_cloud_config

        config = build_cloud_config(
            "browserstack",
            project="My App",
            build="CI #42",
            device="Google Pixel 7",
            os_version="13.0",
        )
        # Use config.server_url and config.capabilities with build_driver_config
    """
    normalized = provider.lower().strip()

    if normalized in {"browserstack"}:
        return _browserstack_config(**kwargs)
    if normalized in {"saucelabs", "sauce"}:
        return _saucelabs_config(**kwargs)
    if normalized in {"aws", "aws_device_farm"}:
        return _aws_config(**kwargs)

    supported = ", ".join(sorted({"browserstack", "saucelabs", "aws"}))
    msg = f"Unknown cloud provider {provider!r}. Supported: {supported}"
    raise ConfigurationError(msg)


def apply_cloud_config(
    capabilities: dict[str, Any],
    cloud: CloudConfig,
) -> dict[str, Any]:
    """Merge cloud-provider capabilities into an existing capability dict.

    Returns a new dict; does not mutate the input.
    """
    merged = dict(capabilities)
    merged.update(cloud.capabilities)
    return merged
