"""Pytest plugin that provides appium-pytest-kit fixtures and hooks."""


from typing import Any

import pytest
from _pytest.config import Config
from _pytest.stash import StashKey

from appium_pytest_kit._internal.reporting import SessionReportCollector
from appium_pytest_kit._internal.server import AppiumServerInfo, AppiumServerManager
from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.driver import DriverConfig, build_driver_config, create_driver
from appium_pytest_kit.hooks import AppiumPytestKitHookSpecs
from appium_pytest_kit.settings import AppiumPytestKitSettings, apply_cli_overrides, load_settings
from appium_pytest_kit.waits import Waiter

SETTINGS_KEY: StashKey[AppiumPytestKitSettings] = StashKey()
REPORTER_KEY: StashKey[SessionReportCollector | None] = StashKey()


def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    """Register appium-pytest-kit custom hook specifications."""

    pluginmanager.add_hookspecs(AppiumPytestKitHookSpecs)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Expose CLI overrides that take precedence over env settings."""

    group = parser.getgroup("appium-pytest-kit")

    group.addoption("--app-env-file", action="store", default=None)
    group.addoption("--app-platform", action="store", default=None)
    group.addoption("--appium-url", action="store", default=None)
    group.addoption("--app-device-name", action="store", default=None)
    group.addoption("--app-platform-version", action="store", default=None)
    group.addoption("--app-udid", action="store", default=None)
    group.addoption("--app-app", action="store", default=None)
    group.addoption("--app-app-package", action="store", default=None)
    group.addoption("--app-app-activity", action="store", default=None)
    group.addoption("--app-bundle-id", action="store", default=None)
    group.addoption("--app-capabilities-json", action="store", default=None)
    group.addoption("--app-implicit-wait", action="store", default=None)

    group.addoption(
        "--app-manage-appium-server",
        action="store_true",
        default=None,
        dest="app_manage_appium_server",
    )
    group.addoption(
        "--no-app-manage-appium-server",
        action="store_false",
        default=None,
        dest="app_manage_appium_server",
    )
    group.addoption(
        "--app-reporting-enabled",
        action="store_true",
        default=None,
        dest="app_reporting_enabled",
    )
    group.addoption(
        "--no-app-reporting-enabled",
        action="store_false",
        default=None,
        dest="app_reporting_enabled",
    )

    group.addoption(
        "--app-override",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Arbitrary APP_ setting override (repeatable)",
    )


def _parse_inline_override(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        msg = f"Invalid --app-override format: '{raw}'. Expected KEY=VALUE"
        raise pytest.UsageError(msg)
    key, value = raw.split("=", 1)
    return key.strip(), value.strip()


def _collect_cli_overrides(config: Config) -> dict[str, Any]:
    overrides: dict[str, Any] = {
        key: value
        for key, value in {
            "app_platform": config.getoption("app_platform"),
            "appium_url": config.getoption("appium_url"),
            "app_device_name": config.getoption("app_device_name"),
            "app_platform_version": config.getoption("app_platform_version"),
            "app_udid": config.getoption("app_udid"),
            "app_app": config.getoption("app_app"),
            "app_app_package": config.getoption("app_app_package"),
            "app_app_activity": config.getoption("app_app_activity"),
            "app_bundle_id": config.getoption("app_bundle_id"),
            "app_capabilities_json": config.getoption("app_capabilities_json"),
            "app_implicit_wait": config.getoption("app_implicit_wait"),
            "app_manage_appium_server": config.getoption("app_manage_appium_server"),
            "app_reporting_enabled": config.getoption("app_reporting_enabled"),
        }.items()
        if value is not None
    }

    for raw_override in config.getoption("app_override"):
        key, value = _parse_inline_override(raw_override)
        overrides[key] = value

    return overrides


def pytest_configure(config: Config) -> None:
    """Load and stash framework settings at session start."""

    env_file = config.getoption("app_env_file")
    settings = load_settings(env_file=env_file)
    settings = apply_cli_overrides(settings, _collect_cli_overrides(config))

    maybe_replacement = config.pluginmanager.hook.pytest_appium_pytest_kit_configure_settings(
        settings=settings
    )
    if maybe_replacement is not None:
        settings = maybe_replacement

    config.stash[SETTINGS_KEY] = settings

    if settings.reporting_enabled:
        config.stash[REPORTER_KEY] = SessionReportCollector(output_dir=settings.report_dir)
    else:
        config.stash[REPORTER_KEY] = None


@pytest.fixture(scope="session")
def settings(pytestconfig: Config) -> AppiumPytestKitSettings:
    """Resolved appium-pytest-kit settings fixture."""

    return pytestconfig.stash[SETTINGS_KEY]


@pytest.fixture(scope="session")
def appium_server(settings) -> AppiumServerInfo:
    """Resolved Appium server fixture with optional local lifecycle management."""

    manager = AppiumServerManager(settings)
    info = manager.resolve()
    try:
        yield info
    finally:
        manager.stop()


@pytest.fixture
def driver(settings, appium_server: AppiumServerInfo, request: pytest.FixtureRequest):
    """Create and yield an Appium driver for each test function."""

    config = build_driver_config(settings, server_url=appium_server.url)
    capabilities = dict(config.capabilities)

    for extension_caps in request.config.pluginmanager.hook.pytest_appium_pytest_kit_capabilities(
        capabilities=capabilities,
        settings=settings,
    ):
        if extension_caps:
            capabilities.update(dict(extension_caps))

    final_config = DriverConfig(
        server_url=config.server_url,
        capabilities=capabilities,
        implicit_wait=config.implicit_wait,
    )

    created_driver = create_driver(final_config)
    request.config.pluginmanager.hook.pytest_appium_pytest_kit_driver_created(
        driver=created_driver,
        settings=settings,
    )

    try:
        yield created_driver
    finally:
        created_driver.quit()


@pytest.fixture
def waiter(driver, settings) -> Waiter:
    """Reusable waiter fixture built around current driver instance."""

    return Waiter(driver, default_timeout=max(settings.implicit_wait, 10.0))


@pytest.fixture
def actions(driver, waiter: Waiter) -> MobileActions:
    """Reusable app-agnostic actions fixture."""

    return MobileActions(driver=driver, waiter=waiter)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    """Collect call-phase report results when basic reporting is enabled."""

    report = yield
    reporter = item.config.stash.get(REPORTER_KEY, None)
    if reporter is not None:
        reporter.record(report)
    return report


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Flush optional report output at end of session."""

    reporter = session.config.stash.get(REPORTER_KEY, None)
    if reporter is not None:
        reporter.flush()
