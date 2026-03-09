---
name: fixture-design
description: Design pytest fixtures with correct scope, teardown, stash-based state, xdist safety, and retry awareness.
---

# Fixture Design

## Use This Skill When

- Creating a new pytest fixture for the framework
- Refactoring existing fixture scope or teardown
- Adding xdist worker isolation to a fixture
- Making a fixture retry-aware (pytest-retry compatible)
- Debugging fixture teardown ordering issues

## Design Process

1. **Define the resource**: what does the fixture provide? (driver, config, connection, page object)
2. **Choose scope**: `function` (per-test, safest), `session` (shared, faster), `class` (rare)
3. **Design setup**: what preconditions are needed? Can setup fail gracefully?
4. **Design teardown**: use `yield` for cleanup; handle partial-setup failures
5. **State management**: use `pytest.Config.stash` with typed `StashKey`, not globals
6. **xdist safety**: no shared mutable state; use worker-specific keys/ports if needed
7. **Retry awareness**: if applicable, register in retry registry so retries reuse the resource

## Scope Decision Guide

| Scope | Use when | Examples |
|-------|----------|---------|
| `function` | Resource must be fresh per test | `driver`, `waiter`, `actions`, `page_factory` |
| `session` | Resource is expensive and stateless | `settings`, `device_info`, `appium_server` |
| `class` | Tests in a class share setup | Rare — prefer function scope |

## Implementation Patterns

### Basic fixture with teardown
```python
@pytest.fixture(scope="function")
def my_resource(settings):
    resource = create_resource(settings)
    yield resource
    resource.cleanup()
```

### Stash-based state (session fixtures)
```python
MY_KEY: StashKey[MyType] = StashKey()

@pytest.fixture(scope="session")
def my_shared(request):
    obj = MyType()
    request.config.stash[MY_KEY] = obj
    yield obj
```

### xdist worker isolation
```python
@pytest.fixture(scope="session")
def isolated_port(request):
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    base_port = 4723
    offset = int(worker_id.replace("gw", "")) if worker_id != "master" else 0
    return base_port + offset
```

### Retry-aware registry
```python
RETRY_REGISTRY_KEY: StashKey[dict] = StashKey()

@pytest.fixture(scope="function")
def reusable_driver(request, settings):
    registry = request.config.stash.get(RETRY_REGISTRY_KEY, {})
    node_id = request.node.nodeid
    if node_id in registry:
        yield registry[node_id]
        return
    driver = create_driver(settings)
    registry[node_id] = driver
    request.config.stash[RETRY_REGISTRY_KEY] = registry
    yield driver
```

## Rules

- Never use module-level globals for fixture state — use `Config.stash`
- Always add teardown for resources that hold connections or processes
- Session fixtures must not depend on function-scoped fixtures
- Fixtures must be safe under `pytest-xdist` parallel execution
- Check stash key existence safely: `stash.get(KEY, default)` or `KEY in stash`
- Document new fixtures in `docs/fixtures.md`

## Anti-Patterns

- Global `driver` variable shared across tests
- Teardown that silently swallows exceptions
- Session-scoped fixture that assumes single-worker execution
- Fixture that modifies `Config.stash` without a typed `StashKey`
- Circular fixture dependencies (A depends on B depends on A)

## Definition of Done

- Fixture has correct scope for its lifecycle
- Teardown handles partial-setup failures
- State stored via typed `StashKey` in `Config.stash`
- xdist-safe (no shared mutable state)
- Unit test covering setup, teardown, and edge cases
- Documented in `docs/fixtures.md`
