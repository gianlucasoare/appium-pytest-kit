"""Local Appium server lifecycle helpers."""


import logging
from dataclasses import dataclass

from appium_pytest_kit.errors import ConfigurationError
from appium_pytest_kit.settings import AppiumPytestKitSettings

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AppiumServerInfo:
    """Resolved Appium server information."""

    url: str
    managed: bool


class AppiumServerManager:
    """Starts/stops a local Appium server when enabled by settings."""

    def __init__(self, settings: AppiumPytestKitSettings) -> None:
        self._settings = settings
        self._service = None

    def _build_managed_url(self) -> str:
        path = self._settings.appium_base_path.rstrip("/") or "/"
        base_url = f"http://{self._settings.appium_host}:{self._settings.appium_port}"
        return base_url if path == "/" else f"{base_url}{path}"

    @staticmethod
    def _flag(service: object, attribute: str) -> bool:
        value = getattr(service, attribute, False)
        return bool(value() if callable(value) else value)

    def resolve(self) -> AppiumServerInfo:
        """Resolve server details and start local Appium when enabled."""

        if not self._settings.manage_appium_server:
            return AppiumServerInfo(url=self._settings.appium_url, managed=False)

        try:
            from appium.webdriver.appium_service import AppiumService
        except ImportError as exc:  # pragma: no cover - import boundary
            msg = (
                "AppiumService is unavailable. Ensure Appium-Python-Client is installed "
                "to use APP_MANAGE_APPIUM_SERVER=true."
            )
            raise ConfigurationError(msg) from exc

        service = AppiumService()
        args: list[str] = [
            "--address",
            self._settings.appium_host,
            "--port",
            str(self._settings.appium_port),
            "--base-path",
            self._settings.appium_base_path,
            *self._settings.appium_server_args,
        ]
        timeout_ms = max(int(self._settings.appium_start_timeout * 1000), 1)
        logger.info(
            "server:starting  host=%s  port=%d  timeout=%dms",
            self._settings.appium_host,
            self._settings.appium_port,
            timeout_ms,
        )
        service.start(args=args, timeout_ms=timeout_ms)

        if not self._flag(service, "is_running"):
            msg = "Failed to start managed Appium server"
            raise ConfigurationError(msg)

        url = self._build_managed_url()
        logger.info("server:ready  url=%s", url)
        self._service = service
        return AppiumServerInfo(url=url, managed=True)

    def stop(self) -> None:
        """Stop managed Appium process when running."""

        if self._service is None:
            return
        if self._flag(self._service, "is_running"):
            logger.info("server:stopping")
            self._service.stop()
        self._service = None
