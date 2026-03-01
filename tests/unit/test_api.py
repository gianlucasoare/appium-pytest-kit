"""Unit tests for the lightweight API client helpers."""

import io
from urllib.error import HTTPError, URLError

import pytest

from appium_pytest_kit.api import ApiClient, ApiResponse
from appium_pytest_kit.errors import ApiRequestError


class _FakeResponse:
    def __init__(
        self,
        *,
        status: int = 200,
        body: bytes = b"",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self._body = body
        self.headers = headers or {}

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        _ = (exc_type, exc, tb)
        return False


def test_get_builds_query_params_and_parses_json(monkeypatch) -> None:
    client = ApiClient("http://localhost:8080")
    observed: dict[str, object] = {}

    def _fake_urlopen(request, *, timeout):
        observed["url"] = request.full_url
        observed["method"] = request.get_method()
        observed["timeout"] = timeout
        return _FakeResponse(
            status=200,
            body=b'{"ok": true}',
            headers={"content-type": "application/json"},
        )

    monkeypatch.setattr("appium_pytest_kit.api.urlopen", _fake_urlopen)

    response = client.get(
        "/health?from=client",
        params={"verbose": True, "limit": 5},
        expected_status=200,
    )
    assert isinstance(response, ApiResponse)
    assert response.json() == {"ok": True}
    assert observed["method"] == "GET"
    assert observed["timeout"] == 30.0
    assert str(observed["url"]) == "http://localhost:8080/health?from=client&verbose=true&limit=5"


def test_post_json_sets_content_type_and_body(monkeypatch) -> None:
    client = ApiClient("http://localhost:8080", timeout=10.0)
    observed: dict[str, object] = {}

    def _fake_urlopen(request, *, timeout):
        observed["method"] = request.get_method()
        observed["timeout"] = timeout
        observed["data"] = request.data
        observed["headers"] = {k.lower(): v for k, v in request.header_items()}
        return _FakeResponse(status=201, body=b'{"id": "123"}')

    monkeypatch.setattr("appium_pytest_kit.api.urlopen", _fake_urlopen)

    response = client.post(
        "/users",
        json={"name": "alice"},
        expected_status=(200, 201),
    )
    assert response.status_code == 201
    assert response.json() == {"id": "123"}
    assert observed["method"] == "POST"
    assert observed["timeout"] == 10.0
    assert observed["data"] == b'{"name": "alice"}'
    assert observed["headers"]["content-type"] == "application/json"


def test_expected_status_raises_on_unexpected_response(monkeypatch) -> None:
    client = ApiClient("http://localhost:8080")

    def _fake_urlopen(_request, *, timeout):
        _ = timeout
        return _FakeResponse(status=204, body=b"")

    monkeypatch.setattr("appium_pytest_kit.api.urlopen", _fake_urlopen)

    with pytest.raises(ApiRequestError) as exc_info:
        client.get("/health", expected_status=200)
    assert exc_info.value.status_code == 204
    assert "unexpected status code" in str(exc_info.value)


def test_http_error_is_wrapped(monkeypatch) -> None:
    client = ApiClient("http://localhost:8080")

    def _fake_urlopen(_request, *, timeout):
        _ = timeout
        raise HTTPError(
            url="http://localhost:8080/missing",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"missing"}'),
        )

    monkeypatch.setattr("appium_pytest_kit.api.urlopen", _fake_urlopen)

    with pytest.raises(ApiRequestError) as exc_info:
        client.get("/missing")
    assert exc_info.value.status_code == 404
    assert "HTTP 404" in str(exc_info.value)


def test_url_error_is_wrapped(monkeypatch) -> None:
    client = ApiClient("http://localhost:8080")

    def _fake_urlopen(_request, *, timeout):
        _ = timeout
        raise URLError("connection refused")

    monkeypatch.setattr("appium_pytest_kit.api.urlopen", _fake_urlopen)

    with pytest.raises(ApiRequestError) as exc_info:
        client.get("/health")
    assert "connection refused" in str(exc_info.value)


def test_invalid_base_url_raises_value_error() -> None:
    with pytest.raises(ValueError):
        ApiClient("localhost:8080")
