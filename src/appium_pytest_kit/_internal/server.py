"""Local Appium server lifecycle helpers."""


import json
import logging
import os
import re
from dataclasses import dataclass
from urllib.error import URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import urlopen

from appium_pytest_kit.errors import ConfigurationError
from appium_pytest_kit.settings import AppiumPytestKitSettings

logger = logging.getLogger(__name__)
_WORKER_INDEX_RE = re.compile(r"(\d+)$")


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
        self._worker_id = os.getenv("PYTEST_XDIST_WORKER") or ""
        self._worker_index = self._parse_worker_index(self._worker_id)

    @staticmethod
    def _parse_worker_index(worker_id: str) -> int:
        if not worker_id:
            return 0
        match = _WORKER_INDEX_RE.search(worker_id)
        return int(match.group(1)) if match else 0

    def _build_managed_url(self, port: int) -> str:
        path = self._settings.appium_base_path.rstrip("/") or "/"
        base_url = f"http://{self._settings.appium_host}:{port}"
        return base_url if path == "/" else f"{base_url}{path}"

    @staticmethod
    def _flag(service: object, attribute: str) -> bool:
        value = getattr(service, attribute, False)
        return bool(value() if callable(value) else value)

    @staticmethod
    def _status_endpoint(server_url: str) -> str:
        parsed = urlparse(server_url)
        base_path = parsed.path.rstrip("/")
        path = f"{base_path}/status" if base_path else "/status"
        return urlunparse(parsed._replace(path=path, params="", query="", fragment=""))

    def _preflight_external_server(self) -> None:
        timeout = max(float(self._settings.appium_start_timeout), 1.0)
        status_url = self._status_endpoint(self._settings.appium_url)
        logger.info("server:preflight  url=%s  timeout=%.1fs", status_url, timeout)

        try:
            with urlopen(status_url, timeout=timeout) as response:  # nosec B310
                payload = response.read().decode("utf-8", errors="replace")
        except (OSError, URLError) as exc:
            msg = (
                "External Appium server preflight failed. "
                f"Could not reach {status_url}: {exc}"
            )
            raise ConfigurationError(msg) from exc

        try:
            decoded = json.loads(payload)
        except ValueError as exc:
            msg = (
                "External Appium server preflight failed. "
                f"{status_url} did not return valid JSON."
            )
            raise ConfigurationError(msg) from exc

        value = decoded.get("value") if isinstance(decoded, dict) else None
        if isinstance(value, dict):
            ready = value.get("ready")
            if ready is False:
                msg = (
                    "External Appium server preflight failed. "
                    f"{status_url} reported ready=false."
                )
                raise ConfigurationError(msg)

    def resolve(self) -> AppiumServerInfo:
        """Resolve server details and start local Appium when enabled."""

        if not self._settings.manage_appium_server:
            if self._settings.appium_preflight_status:
                self._preflight_external_server()
            return AppiumServerInfo(url=self._settings.appium_url, managed=False)

        try:
            from appium.webdriver.appium_service import AppiumService
        except ImportError as exc:  # pragma: no cover - import boundary
            msg = (
                "AppiumService is unavailable. Ensure Appium-Python-Client is installed "
                "to use APP_MANAGE_APPIUM_SERVER=true."
            )
            raise ConfigurationError(msg) from exc

        effective_port = self._settings.appium_port + self._worker_index
        service = AppiumService()
        args: list[str] = [
            "--address",
            self._settings.appium_host,
            "--port",
            str(effective_port),
            "--base-path",
            self._settings.appium_base_path,
            *self._settings.appium_server_args,
        ]
        timeout_ms = max(int(self._settings.appium_start_timeout * 1000), 1)
        logger.info(
            "server:starting  host=%s  port=%d  timeout=%dms  worker=%s",
            self._settings.appium_host,
            effective_port,
            timeout_ms,
            self._worker_id or "master",
        )
        service.start(args=args, timeout_ms=timeout_ms)

        if not self._flag(service, "is_running"):
            msg = "Failed to start managed Appium server"
            raise ConfigurationError(msg)

        url = self._build_managed_url(effective_port)
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
