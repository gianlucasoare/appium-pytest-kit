"""Simple HTTP API helpers for endpoint testing from pytest suites."""

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from appium_pytest_kit.errors import ApiRequestError

_JsonValue = Any


@dataclass(frozen=True, slots=True)
class ApiResponse:
    """HTTP response object returned by :class:`ApiClient`."""

    status_code: int
    headers: dict[str, str]
    body: bytes
    url: str

    @property
    def text(self) -> str:
        """Decode response body as UTF-8 with replacement for invalid bytes."""
        return self.body.decode("utf-8", errors="replace")

    def json(self) -> _JsonValue:
        """Parse body as JSON."""
        return json.loads(self.text)


class ApiClient:
    """Small synchronous API client for endpoint checks."""

    def __init__(
        self,
        base_url: str,
        *,
        default_headers: Mapping[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        if not base_url.strip():
            msg = "base_url must not be empty"
            raise ValueError(msg)

        parsed = urlsplit(base_url)
        if not parsed.scheme or not parsed.netloc:
            msg = "base_url must include scheme and host, e.g. http://127.0.0.1:8000"
            raise ValueError(msg)

        self.base_url = base_url.rstrip("/")
        self.default_headers = dict(default_headers or {})
        self.timeout = timeout

    def _build_url(self, path: str, params: Mapping[str, Any] | None = None) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            resolved = path
        else:
            normalized_path = path if path.startswith("/") else f"/{path}"
            resolved = f"{self.base_url}{normalized_path}"

        if not params:
            return resolved

        parsed = urlsplit(resolved)
        pairs: list[tuple[str, str]] = list(parse_qsl(parsed.query, keep_blank_values=True))

        for key, value in params.items():
            if value is None:
                continue
            if isinstance(value, (list, tuple, set)):
                for item in value:
                    pairs.append((str(key), self._stringify_param(item)))
                continue
            pairs.append((str(key), self._stringify_param(value)))

        query = urlencode(pairs, doseq=True)
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))

    @staticmethod
    def _stringify_param(value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    @staticmethod
    def _normalize_expected_status(expected_status: int | Sequence[int] | None) -> set[int] | None:
        if expected_status is None:
            return None
        if isinstance(expected_status, int):
            return {expected_status}
        return {int(item) for item in expected_status}

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        json_body: _JsonValue | None = None,
        data: bytes | str | None = None,
        timeout: float | None = None,
        expected_status: int | Sequence[int] | None = None,
    ) -> ApiResponse:
        if json_body is not None and data is not None:
            msg = "pass either json_body or data, not both"
            raise ValueError(msg)

        method_name = method.upper().strip()
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)

        payload: bytes | None = None
        if json_body is not None:
            payload = json.dumps(json_body).encode("utf-8")
            merged_headers.setdefault("Content-Type", "application/json")
        elif isinstance(data, str):
            payload = data.encode("utf-8")
        elif isinstance(data, bytes):
            payload = data
        elif data is not None:
            msg = "data must be bytes, str or None"
            raise TypeError(msg)

        url = self._build_url(path, params=params)
        request = Request(url=url, method=method_name, data=payload, headers=merged_headers)
        effective_timeout = self.timeout if timeout is None else timeout

        try:
            with urlopen(request, timeout=effective_timeout) as response:  # nosec B310
                body = response.read()
                raw_status = getattr(response, "status", None)
                if raw_status is None:
                    getcode = getattr(response, "getcode", None)
                    raw_status = getcode() if callable(getcode) else None
                if raw_status is None:
                    raise ApiRequestError(
                        "response did not expose an HTTP status code",
                        method=method_name,
                        url=url,
                    )
                status = int(raw_status)
                response_headers = {str(k): str(v) for k, v in response.headers.items()}
        except HTTPError as exc:
            body = exc.read() if hasattr(exc, "read") else b""
            snippet = body[:300].decode("utf-8", errors="replace").strip()
            message = f"HTTP {exc.code} returned by endpoint"
            if snippet:
                message = f"{message}: {snippet}"
            raise ApiRequestError(
                message,
                method=method_name,
                url=url,
                status_code=int(exc.code),
            ) from exc
        except URLError as exc:
            raise ApiRequestError(str(exc.reason), method=method_name, url=url) from exc
        except OSError as exc:
            raise ApiRequestError(str(exc), method=method_name, url=url) from exc

        api_response = ApiResponse(
            status_code=status,
            headers=response_headers,
            body=body,
            url=url,
        )

        expected = self._normalize_expected_status(expected_status)
        if expected is not None and api_response.status_code not in expected:
            allowed = ", ".join(str(code) for code in sorted(expected))
            raise ApiRequestError(
                f"unexpected status code; expected one of: {allowed}",
                method=method_name,
                url=url,
                status_code=api_response.status_code,
            )
        return api_response

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        expected_status: int | Sequence[int] | None = None,
    ) -> ApiResponse:
        return self.request(
            "GET",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
            expected_status=expected_status,
        )

    def post(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        json: _JsonValue | None = None,
        data: bytes | str | None = None,
        timeout: float | None = None,
        expected_status: int | Sequence[int] | None = None,
    ) -> ApiResponse:
        return self.request(
            "POST",
            path,
            params=params,
            headers=headers,
            json_body=json,
            data=data,
            timeout=timeout,
            expected_status=expected_status,
        )

    def put(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        json: _JsonValue | None = None,
        data: bytes | str | None = None,
        timeout: float | None = None,
        expected_status: int | Sequence[int] | None = None,
    ) -> ApiResponse:
        return self.request(
            "PUT",
            path,
            params=params,
            headers=headers,
            json_body=json,
            data=data,
            timeout=timeout,
            expected_status=expected_status,
        )

    def patch(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        json: _JsonValue | None = None,
        data: bytes | str | None = None,
        timeout: float | None = None,
        expected_status: int | Sequence[int] | None = None,
    ) -> ApiResponse:
        return self.request(
            "PATCH",
            path,
            params=params,
            headers=headers,
            json_body=json,
            data=data,
            timeout=timeout,
            expected_status=expected_status,
        )

    def delete(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: float | None = None,
        expected_status: int | Sequence[int] | None = None,
    ) -> ApiResponse:
        return self.request(
            "DELETE",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
            expected_status=expected_status,
        )
