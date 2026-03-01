# API Testing Step By Step

This guide is for first-time API automation users. It takes you from zero setup
to reliable endpoint checks and hybrid API + mobile flows.

`appium-pytest-kit` provides:

- `ApiClient` for HTTP requests
- `ApiResponse` for response handling (`status_code`, `text`, `json()`)
- `ApiRequestError` for network/status failures with context

---

## 1. Understand where API tests fit

Use API tests for:

- backend contract checks (`/health`, `/auth/login`, `/orders`)
- fast setup/teardown of test data before UI tests
- validating side effects after UI actions

Keep API tests in `tests/api/` and UI tests in `tests/android/` or `tests/ios/`.

---

## 2. Scaffold a project with API support

Create a new project:

```bash
pip install appium-pytest-kit
appium-pytest-kit-init --framework --root my-project
cd my-project
```

The scaffold now includes:

```text
api/client.py
tests/api/test_health.py
conftest.py  (with api_client fixture)
```

---

## 3. Configure API environment variables

The generated `api/client.py` reads:

- `API_BASE_URL` (default: `http://127.0.0.1:8000`)
- `API_TOKEN` (optional bearer token)

Run tests with explicit values:

```bash
API_BASE_URL=http://localhost:8080 pytest tests/api -m api -v
```

Authenticated API:

```bash
API_BASE_URL=https://staging.example.com \
API_TOKEN=your_token_here \
pytest tests/api -m api -v
```

Never commit real tokens to Git.

---

## 4. Write your first endpoint test

Example health check:

```python
# tests/api/test_health.py
import pytest


@pytest.mark.api
def test_health_endpoint(api_client) -> None:
    response = api_client.get("/health", expected_status=200)
    payload = response.json()
    assert payload["ok"] is True
```

Key points:

- `expected_status=200` fails fast when contract changes.
- `response.json()` parses JSON payload.
- `@pytest.mark.api` lets you run only API tests.

Run it:

```bash
pytest tests/api/test_health.py -v
pytest -m api -v
```

---

## 5. Build a reusable API client fixture

Scaffold already gives this fixture:

```python
@pytest.fixture(scope="session")
def api_client() -> ApiClient:
    from api.client import get_api_client
    return get_api_client()
```

You can extend `api/client.py` with project defaults:

```python
import os
from appium_pytest_kit.api import ApiClient


def get_api_client() -> ApiClient:
    base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    token = os.getenv("API_TOKEN")
    tenant = os.getenv("API_TENANT")

    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if tenant:
        headers["X-Tenant"] = tenant

    return ApiClient(base_url=base_url, default_headers=headers, timeout=20.0)
```

---

## 6. Cover common request patterns

### GET with query params

```python
def test_list_orders(api_client) -> None:
    response = api_client.get(
        "/orders",
        params={"limit": 20, "status": "OPEN"},
        expected_status=200,
    )
    data = response.json()
    assert isinstance(data["items"], list)
```

### POST with JSON

```python
def test_create_order(api_client) -> None:
    response = api_client.post(
        "/orders",
        json={"productId": "coffee-01", "qty": 2},
        expected_status=201,
    )
    created = response.json()
    assert created["qty"] == 2
```

### Multiple accepted status codes

```python
def test_idempotent_create(api_client) -> None:
    response = api_client.post(
        "/orders/sync",
        json={"externalId": "abc-123"},
        expected_status={200, 201},
    )
    assert response.status_code in {200, 201}
```

---

## 7. Validate errors and negative paths

Always test unhappy paths:

```python
def test_create_order_validation_error(api_client) -> None:
    response = api_client.post(
        "/orders",
        json={"productId": "", "qty": -1},
        expected_status=400,
    )
    body = response.json()
    assert "errors" in body
```

If the response status does not match `expected_status`, `ApiRequestError` is raised.

---

## 8. Add structured test data patterns

For maintainability:

- keep payload builders in `tests/api/builders.py`
- avoid large inline JSON blobs in each test
- use deterministic identifiers (`order-e2e-001`)

Example builder:

```python
def order_payload(*, product_id: str = "coffee-01", qty: int = 1) -> dict[str, object]:
    return {"productId": product_id, "qty": qty}
```

---

## 9. Hybrid flow: API setup, UI verification

This is one of the highest-value patterns.

```python
import pytest


@pytest.mark.integration
def test_order_created_via_api_visible_in_app(api_client, actions):
    created = api_client.post(
        "/orders",
        json={"productId": "coffee-01", "qty": 1},
        expected_status=201,
    ).json()

    order_id = created["id"]
    actions.open_deep_link(f"myapp://orders/{order_id}", app_id="com.example.myapp")
    # assert order details on screen...
```

Why this is better:

- no slow UI setup for prerequisite data
- less flakiness
- faster feedback loop

---

## 10. Organize suites and marks

Suggested marks:

- `@pytest.mark.api` for API-only tests
- `@pytest.mark.integration` for API + UI flows
- `@pytest.mark.smoke` for critical endpoint checks

Suggested layout:

```text
tests/
  api/
    test_health.py
    test_auth.py
    test_orders.py
  android/
  ios/
```

---

## 11. CI usage

Run fast API lane first:

```bash
pytest -m api -q
```

Then run UI lanes:

```bash
pytest -m "not api" -q
```

If API lane fails, block release early. It is usually the fastest signal.

---

## 12. Troubleshooting

### `ApiRequestError: connection refused`

- API is not running
- wrong `API_BASE_URL`
- local firewall/network issue

### `ApiRequestError: unexpected status code`

- endpoint contract changed
- auth missing/expired
- stale test data preconditions

### JSON parsing error on `response.json()`

- endpoint returned plain text/HTML
- inspect `response.text` first and assert `content-type` expectations

---

## API reference quick notes

`ApiClient` methods:

- `get(path, params=..., headers=..., timeout=..., expected_status=...)`
- `post(path, json=..., data=..., params=..., expected_status=...)`
- `put(...)`, `patch(...)`, `delete(...)`
- `request(method, path, ...)` for custom verbs

`ApiResponse`:

- `status_code`
- `headers`
- `body`
- `text`
- `json()`

---

## Rules for stable API tests

- Assert status code in every test (`expected_status`).
- Assert business outcome, not only response shape.
- Keep tests independent and idempotent.
- Prefer API setup over UI setup for prerequisites.
- Use environment variables for secrets and base URLs.
