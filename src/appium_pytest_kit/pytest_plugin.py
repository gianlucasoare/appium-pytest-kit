"""Pytest plugin that provides appium-pytest-kit fixtures and hooks."""


import logging
from typing import Any

import pytest
from _pytest.config import Config
from _pytest.stash import StashKey

from appium_pytest_kit._internal.device_resolver import (
    DeviceInfo,
    DeviceResolver,
    validate_launch_config,
)
from appium_pytest_kit._internal.diagnostics import (
    attach_to_allure,
    capture_device_logs,
    capture_page_source,
    capture_screenshot,
)
from appium_pytest_kit._internal.reporting import SessionReportCollector
from appium_pytest_kit._internal.server import AppiumServerInfo, AppiumServerManager
from appium_pytest_kit._internal.video import ScreenRecorder
from appium_pytest_kit.actions import MobileActions
from appium_pytest_kit.driver import DriverConfig, build_driver_config, create_driver
from appium_pytest_kit.errors import ConfigurationError
from appium_pytest_kit.hooks import AppiumPytestKitHookSpecs
from appium_pytest_kit.settings import (
    AppiumPytestKitSettings,
    apply_cli_overrides,
    load_settings,
    validate_capabilities_for_strict,
)
from appium_pytest_kit.waits import Waiter

logger = logging.getLogger(__name__)

SETTINGS_KEY: StashKey[AppiumPytestKitSettings] = StashKey()
REPORTER_KEY: StashKey[SessionReportCollector | None] = StashKey()
DRIVER_KEY: StashKey[Any] = StashKey()
RECORDER_KEY: StashKey[ScreenRecorder | None] = StashKey()
DEVICE_INFO_KEY: StashKey[DeviceInfo | None] = StashKey()

# Retry-aware session reuse.
# Maps nodeid -> live driver so retries reuse the same Appium session.
RETRY_DRIVER_REGISTRY_KEY: StashKey[dict[str, Any]] = StashKey()
# Maps nodeid -> recorder created for the first attempt.
RETRY_RECORDER_REGISTRY_KEY: StashKey[dict[str, ScreenRecorder | None]] = StashKey()
# Maps nodeid -> number of call-phase failures seen so far.
RETRY_FAIL_COUNT_KEY: StashKey[dict[str, int]] = StashKey()
# Set on a node's stash when the driver must survive the current teardown
# because another retry attempt is coming for the same test.
KEEP_DRIVER_ALIVE_KEY: StashKey[bool] = StashKey()


def _get_max_retries(item: pytest.Item) -> int:
    """Return the maximum number of *extra* retries configured for *item*.

    Checks ``@pytest.mark.flaky(retries=N)`` first (pytest-retry's marker),
    then the ``--retries`` CLI option added by pytest-retry.  Returns 0 when
    pytest-retry is not installed or no retry is configured.

    The ``retries`` value is the number of *re-tries*, not total attempts
    (matching pytest-retry semantics: ``retries=1`` → 2 total attempts).
    """
    marker = item.get_closest_marker("flaky")
    if marker:
        # @pytest.mark.flaky  → default 1 retry
        # @pytest.mark.flaky(2)  or  @pytest.mark.flaky(retries=2)
        if marker.args:
            retries = int(marker.args[0])
        else:
            retries = int(marker.kwargs.get("retries", 1))
        return max(0, retries)
    try:
        val = item.config.getoption("--retries", default=0)
        return max(0, int(val or 0))
    except (ValueError, TypeError, pytest.UsageError):
        return 0


def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    """Register appium-pytest-kit custom hook specifications."""

    pluginmanager.add_hookspecs(AppiumPytestKitHookSpecs)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Expose CLI overrides that take precedence over env settings."""

    group = parser.getgroup("appium-pytest-kit")

    group.addoption("--app-env-file", action="store", default=None)
    group.addoption("--app-platform", action="store", default=None)
    group.addoption(
        "--app-appium-url",
        "--appium-url",
        action="store",
        default=None,
        dest="appium_url",
        help="Appium server URL. Prefer --app-appium-url; --appium-url is kept as an alias.",
    )
    group.addoption("--app-device-name", action="store", default=None)
    group.addoption("--app-platform-version", action="store", default=None)
    group.addoption("--app-udid", action="store", default=None)
    group.addoption("--app-app", action="store", default=None)
    group.addoption("--app-app-package", action="store", default=None)
    group.addoption("--app-app-activity", action="store", default=None)
    group.addoption("--app-bundle-id", action="store", default=None)
    group.addoption("--app-capabilities-json", action="store", default=None)
    group.addoption("--app-implicit-wait", action="store", default=None)
    group.addoption("--app-session-mode", action="store", default=None)
    group.addoption("--app-device-profile", action="store", default=None)
    group.addoption("--app-devices-yaml", action="store", default=None)
    group.addoption("--app-video-policy", action="store", default=None)
    group.addoption("--app-artifacts-dir", action="store", default=None)

    group.addoption(
        "--app-strict-config",
        action="store_true",
        default=None,
        dest="app_strict_config",
    )
    group.addoption(
        "--no-app-strict-config",
        action="store_false",
        default=None,
        dest="app_strict_config",
    )
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
        "--app-is-simulator",
        action="store_true",
        default=None,
        dest="app_is_simulator",
    )
    group.addoption(
        "--no-app-is-simulator",
        action="store_false",
        default=None,
        dest="app_is_simulator",
    )

    group.addoption(
        "--app-override",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Arbitrary APP_ setting override (repeatable)",
    )

    group.addoption(
        "--app-fail-fast",
        action="store_true",
        default=False,
        dest="app_fail_fast",
        help=(
            "Stop the suite as soon as a test fails after exhausting all retries. "
            "Unlike -x, this allows retries to complete before stopping."
        ),
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
            "app_session_mode": config.getoption("app_session_mode"),
            "app_device_profile": config.getoption("app_device_profile"),
            "app_devices_yaml": config.getoption("app_devices_yaml"),
            "app_video_policy": config.getoption("app_video_policy"),
            "app_artifacts_dir": config.getoption("app_artifacts_dir"),
            "app_is_simulator": config.getoption("app_is_simulator"),
            "app_strict_config": config.getoption("app_strict_config"),
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
    try:
        settings = apply_cli_overrides(settings, _collect_cli_overrides(config))
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc

    maybe_replacement = config.pluginmanager.hook.pytest_appium_pytest_kit_configure_settings(
        settings=settings
    )
    if maybe_replacement is not None:
        settings = maybe_replacement

    config.stash[SETTINGS_KEY] = settings
    config.stash[RETRY_DRIVER_REGISTRY_KEY] = {}
    config.stash[RETRY_RECORDER_REGISTRY_KEY] = {}
    config.stash[RETRY_FAIL_COUNT_KEY] = {}

    if settings.reporting_enabled:
        config.stash[REPORTER_KEY] = SessionReportCollector(output_dir=settings.report_dir)
    else:
        config.stash[REPORTER_KEY] = None


@pytest.fixture(scope="session")
def settings(pytestconfig: Config) -> AppiumPytestKitSettings:
    """Resolved appium-pytest-kit settings fixture."""

    return pytestconfig.stash[SETTINGS_KEY]


@pytest.fixture(scope="session")
def device_info(settings) -> DeviceInfo | None:
    """Resolved device fixture using 3-tier priority (explicit → yaml → auto-detect)."""

    return DeviceResolver(settings).resolve()


@pytest.fixture(scope="session")
def appium_server(settings) -> AppiumServerInfo:
    """Resolved Appium server fixture with optional local lifecycle management."""

    manager = AppiumServerManager(settings)
    info = manager.resolve()
    try:
        yield info
    finally:
        manager.stop()


@pytest.fixture(scope="session")
def _driver_shared(
    settings,
    appium_server: AppiumServerInfo,
    device_info: DeviceInfo | None,
    request: pytest.FixtureRequest,
):
    """Session-scoped driver for clean-session and debug modes.

    Yields None when session_mode is 'clean' so the function-scoped driver
    fixture creates its own per-test driver.
    """

    if settings.session_mode == "clean":
        yield None
        return

    config = _build_final_config(settings, appium_server, request, info=device_info)
    created_driver = create_driver(config)
    logger.info(
        "driver:created  session=%s  platform=%s  mode=%s",
        getattr(created_driver, "session_id", "?"),
        settings.platform,
        settings.session_mode,
    )
    request.config.pluginmanager.hook.pytest_appium_pytest_kit_driver_created(
        driver=created_driver,
        settings=settings,
    )
    try:
        yield created_driver
    finally:
        logger.info("driver:quit  session=%s", getattr(created_driver, "session_id", "?"))
        created_driver.quit()


def _apply_device_info(capabilities: dict, info: DeviceInfo) -> None:
    """Merge DeviceInfo fields into capabilities without overwriting explicit values."""

    if "deviceName" not in capabilities and info.device_name:
        capabilities["deviceName"] = info.device_name
    if "udid" not in capabilities and info.udid:
        capabilities["udid"] = info.udid
    if "platformVersion" not in capabilities and info.platform_version:
        capabilities["platformVersion"] = info.platform_version
    if "automationName" not in capabilities and info.automation_name:
        capabilities["automationName"] = info.automation_name


def _build_final_config(
    settings: AppiumPytestKitSettings,
    appium_server: AppiumServerInfo,
    request: pytest.FixtureRequest,
    info: DeviceInfo | None = None,
) -> DriverConfig:
    """Merge base capabilities with device info + hook extensions and return final config."""

    validate_launch_config(settings)
    config = build_driver_config(settings, server_url=appium_server.url)
    capabilities = dict(config.capabilities)

    if info is not None:
        _apply_device_info(capabilities, info)

    for extension_caps in request.config.pluginmanager.hook.pytest_appium_pytest_kit_capabilities(
        capabilities=capabilities,
        settings=settings,
    ):
        if extension_caps:
            capabilities.update(dict(extension_caps))

    try:
        validate_capabilities_for_strict(capabilities, strict=settings.strict_config)
    except ValueError as exc:
        raise ConfigurationError(str(exc)) from exc

    return DriverConfig(
        server_url=config.server_url,
        capabilities=capabilities,
        implicit_wait=config.implicit_wait,
    )


@pytest.fixture
def driver(settings, appium_server: AppiumServerInfo, device_info: DeviceInfo | None, _driver_shared, request: pytest.FixtureRequest):  # noqa: E501
    """Create and yield an Appium driver for each test function.

    Session lifecycle in 'clean' mode (the default):

    * **First attempt** — a fresh Appium session is created.
    * **Retry attempt** (pytest-retry) — the same session is reused so the
      retry picks up exactly where the failure occurred, with no restart cost.
    * **Retries exhausted / test passes** — the session is quit and the suite
      continues; the next test always starts with a fresh session.

    In 'clean-session' and 'debug' modes the session-scoped driver is reused
    as before, unaffected by retry logic.
    """

    if settings.session_mode != "clean" and _driver_shared is not None:
        # Reuse shared session driver (clean-session / debug mode)
        request.node.stash[DRIVER_KEY] = _driver_shared
        yield _driver_shared
        return

    registry: dict[str, Any] = request.config.stash[RETRY_DRIVER_REGISTRY_KEY]
    recorder_registry: dict[str, ScreenRecorder | None] = request.config.stash[
        RETRY_RECORDER_REGISTRY_KEY
    ]
    nodeid: str = request.node.nodeid

    # Reset the keep-alive flag so a value from the previous attempt on this
    # node cannot bleed into the current invocation.
    request.node.stash[KEEP_DRIVER_ALIVE_KEY] = False

    active_driver: Any = registry.get(nodeid)

    if active_driver is not None:
        # ── Retry attempt: reuse the live session ────────────────────────
        logger.info(
            "driver:reuse  session=%s  node=%s",
            getattr(active_driver, "session_id", "?"),
            nodeid,
        )
        # Keep the recorder created for the first attempt so final artifact
        # capture on pass/final-fail still has a valid recorder instance.
        request.node.stash[RECORDER_KEY] = recorder_registry.get(nodeid)
    else:
        # ── First attempt: start a new session ───────────────────────────
        final_config = _build_final_config(settings, appium_server, request, info=device_info)
        active_driver = create_driver(final_config)
        logger.info(
            "driver:created  session=%s  platform=%s  node=%s",
            getattr(active_driver, "session_id", "?"),
            settings.platform,
            nodeid,
        )
        request.config.pluginmanager.hook.pytest_appium_pytest_kit_driver_created(
            driver=active_driver,
            settings=settings,
        )
        recorder: ScreenRecorder | None = None
        if settings.video_policy in ("always", "failed"):
            recorder = ScreenRecorder()
            recorder.start(active_driver, settings)
        request.node.stash[RECORDER_KEY] = recorder
        registry[nodeid] = active_driver
        recorder_registry[nodeid] = recorder

    request.node.stash[DRIVER_KEY] = active_driver

    try:
        yield active_driver
    finally:
        _teardown_driver(active_driver, nodeid, registry, recorder_registry, request.node.stash)


def _teardown_driver(
    drv: Any,
    nodeid: str,
    registry: dict[str, Any],
    recorder_registry: dict[str, ScreenRecorder | None],
    node_stash,
) -> None:
    """Decide what to do with *drv* after a test (or retry attempt) finishes.

    * ``KEEP_DRIVER_ALIVE`` — a retry is coming; leave the driver in the
      registry so the next attempt finds it.
    * Otherwise — test passed or retries exhausted; quit and deregister so
      the next test starts with a fresh session.
    """
    if node_stash.get(KEEP_DRIVER_ALIVE_KEY, False):
        # Another retry is coming — stay registered, do not quit
        logger.debug("driver:hold  retry pending  node=%s", nodeid)
        return

    registry.pop(nodeid, None)
    recorder_registry.pop(nodeid, None)
    logger.info("driver:quit  session=%s  node=%s", getattr(drv, "session_id", "?"), nodeid)
    _safe_quit(drv)


def _safe_quit(drv: Any) -> None:
    """Quit *drv* without raising, so teardown always completes."""
    try:
        drv.quit()
    except Exception:
        pass


@pytest.fixture
def waiter(driver, settings) -> Waiter:
    """Reusable waiter fixture built around current driver instance."""

    return Waiter(driver, default_timeout=settings.explicit_wait_timeout)


@pytest.fixture
def actions(driver, waiter: Waiter) -> MobileActions:
    """Reusable app-agnostic actions fixture."""

    return MobileActions(driver=driver, waiter=waiter)


@pytest.fixture
def page_factory(driver, waiter: Waiter, actions: MobileActions):
    """Factory fixture for instantiating page objects without boilerplate.

    Usage::

        def test_login(page_factory):
            login = page_factory(LoginPage)
            home  = page_factory(HomePage)
    """

    def _make(page_cls):
        return page_cls(driver, waiter, actions)

    return _make


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    """Collect call-phase report results and capture failure artifacts."""

    report = yield

    # Basic JSON reporting
    reporter = item.config.stash.get(REPORTER_KEY, None)
    if reporter is not None:
        reporter.record(report)

    # Retry-aware session keep-alive: decide before teardown runs whether
    # the driver should survive this fixture scope.
    #
    # This block runs for EVERY call attempt (including mid-retry attempts)
    # because pytest-retry calls pytest_runtest_makereport for each attempt
    # from within its own tryfirst/hookwrapper body, which yields to us.
    # We must set KEEP_DRIVER_ALIVE_KEY here so the driver fixture's teardown
    # (which runs next, inside pytest-retry's retry loop) sees the flag.
    final_failure = False
    if report.when == "call" and report.failed:
        max_retries = _get_max_retries(item)
        final_failure = True  # assume final until proven otherwise

        if max_retries > 0:
            fail_counts: dict[str, int] = item.config.stash[RETRY_FAIL_COUNT_KEY]
            fail_counts[item.nodeid] = fail_counts.get(item.nodeid, 0) + 1
            if fail_counts[item.nodeid] <= max_retries:
                item.stash[KEEP_DRIVER_ALIVE_KEY] = True
                final_failure = False
                logger.info(
                    "retry:keep-alive  attempt=%d/%d  node=%s",
                    fail_counts[item.nodeid],
                    max_retries,
                    item.nodeid,
                )

        if final_failure and item.config.getoption("app_fail_fast", default=False):
            item.session.shouldstop = (
                f"--app-fail-fast: {item.nodeid} failed after all retry attempts"
            )

    # Failure artifact capture (screenshot + page source) on call phase.
    # Only capture on the FINAL failure (not mid-retry), so artifacts reflect
    # the ultimate outcome rather than an intermediate attempt.
    if report.when == "call" and report.failed and final_failure:
        active_driver = item.stash.get(DRIVER_KEY, None)
        settings: AppiumPytestKitSettings | None = item.config.stash.get(SETTINGS_KEY, None)

        if active_driver is not None and settings is not None:
            artifacts_dir = settings.artifacts_dir

            screenshot_path = capture_screenshot(active_driver, item.nodeid, artifacts_dir)
            pagesource_path = capture_page_source(active_driver, item.nodeid, artifacts_dir)
            device_log_path = capture_device_logs(
                active_driver,
                item.nodeid,
                artifacts_dir,
                platform=settings.platform,
                udid=settings.udid,
                is_simulator=settings.is_simulator,
            )

            if screenshot_path and screenshot_path.exists():
                logger.info("artifact:screenshot  %s", screenshot_path)
                attach_to_allure(screenshot_path, "Screenshot on failure", "image/png")
            if pagesource_path and pagesource_path.exists():
                logger.info("artifact:page_source  %s", pagesource_path)
                attach_to_allure(pagesource_path, "Page source on failure", "text/xml")
            if device_log_path and device_log_path.exists():
                logger.info("artifact:device_logs  %s", device_log_path)
                attach_to_allure(device_log_path, "Device logs on failure", "text/plain")

            # Stop video on final failure
            recorder = item.stash.get(RECORDER_KEY, None)
            if recorder is not None and settings.video_policy in ("always", "failed"):
                recorder.stop_and_save(active_driver, item.nodeid, artifacts_dir, settings)

    elif report.when == "call" and not report.failed:
        # Test passed (possibly after retries) — this is always the final outcome.
        active_driver = item.stash.get(DRIVER_KEY, None)
        settings = item.config.stash.get(SETTINGS_KEY, None)
        recorder = item.stash.get(RECORDER_KEY, None)

        if recorder is not None and settings is not None and settings.video_policy == "always":
            if active_driver is not None:
                recorder.stop_and_save(active_driver, item.nodeid, settings.artifacts_dir, settings)

    return report


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Flush optional report output and clean up any orphaned retry drivers."""

    reporter = session.config.stash.get(REPORTER_KEY, None)
    if reporter is not None:
        reporter.flush()

    registry: dict[str, Any] = session.config.stash.get(RETRY_DRIVER_REGISTRY_KEY, {})
    for drv in list(registry.values()):
        _safe_quit(drv)
    registry.clear()
    recorder_registry: dict[str, ScreenRecorder | None] = session.config.stash.get(
        RETRY_RECORDER_REGISTRY_KEY, {}
    )
    recorder_registry.clear()
