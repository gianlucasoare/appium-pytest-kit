"""Data-driven test helpers — load test data from files and generate parametrized cases."""


import json
import logging
from pathlib import Path
from typing import Any

import pytest

logger = logging.getLogger(__name__)


def _load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        msg = (
            f"PyYAML is required to load {path}. "
            "Install it with: pip install appium-pytest-kit[yaml]"
        )
        raise ImportError(msg) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_test_data(
    path: str | Path,
    *,
    platform: str | None = None,
    key: str | None = None,
) -> list[dict[str, Any]]:
    """Load test data from a YAML or JSON file and return a list of dicts.

    Parameters
    ----------
    path:
        Path to a ``.yaml``, ``.yml``, or ``.json`` file.
    platform:
        If set, selects a platform-specific section (e.g. ``"android"`` or ``"ios"``).
        The file should contain a top-level mapping with platform keys.
    key:
        If set, selects a named section from the top-level mapping
        (e.g. ``"login_cases"``).  Applied *after* ``platform`` filtering.

    Returns
    -------
    list[dict[str, Any]]
        Each dict represents one test case.

    Example file (YAML)::

        - name: valid login
          username: user@example.com
          password: Test1234!
          expected: home

        - name: invalid password
          username: user@example.com
          password: wrong
          expected: error

    Example file with platform sections::

        android:
          - name: android deep link
            url: myapp://home
        ios:
          - name: ios universal link
            url: https://myapp.example.com/home
    """
    resolved = Path(path)
    if not resolved.exists():
        msg = f"Test data file not found: {resolved}"
        raise FileNotFoundError(msg)

    suffix = resolved.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        raw = _load_yaml(resolved)
    elif suffix == ".json":
        raw = _load_json(resolved)
    else:
        msg = f"Unsupported test data format: {suffix} (use .yaml, .yml, or .json)"
        raise ValueError(msg)

    if platform is not None:
        if not isinstance(raw, dict):
            msg = f"Expected a mapping with platform keys, got {type(raw).__name__}"
            raise ValueError(msg)
        raw = raw.get(platform, [])

    if key is not None:
        if not isinstance(raw, dict):
            msg = f"Expected a mapping with key {key!r}, got {type(raw).__name__}"
            raise ValueError(msg)
        raw = raw.get(key, [])

    if not isinstance(raw, list):
        msg = f"Expected a list of test cases, got {type(raw).__name__}"
        raise ValueError(msg)

    logger.debug("test_data:loaded  path=%s  count=%d", resolved, len(raw))
    return raw


def from_file(
    path: str | Path,
    *,
    platform: str | None = None,
    key: str | None = None,
    id_field: str = "name",
):
    """Return a ``pytest.mark.parametrize`` decorator that loads cases from a file.

    Parameters
    ----------
    path:
        Path to test data file (.yaml, .yml, or .json).
    platform:
        Optional platform filter (see :func:`load_test_data`).
    key:
        Optional section key (see :func:`load_test_data`).
    id_field:
        Field name used as the test ID. Defaults to ``"name"``.

    Usage::

        @from_file("data/login_cases.yaml")
        def test_login(case, login_page):
            login_page.login(case["username"], case["password"])
            assert login_page.current_screen() == case["expected"]
    """
    cases = load_test_data(path, platform=platform, key=key)
    params = [
        pytest.param(case, id=str(case.get(id_field, i)))
        for i, case in enumerate(cases)
    ]
    return pytest.mark.parametrize("case", params)


def cross_platform(
    platforms: tuple[str, ...] = ("android", "ios"),
):
    """Return a ``pytest.mark.parametrize`` decorator for cross-platform tests.

    Generates one test case per platform, useful for verifying the same
    behavior across Android and iOS.

    Usage::

        @cross_platform()
        def test_login_works(platform, login_page):
            login_page.login("user", "pass")
            assert login_page.is_on_home()

    The ``platform`` parameter is injected as a string fixture value.
    Combine with ``indirect=True`` and a custom fixture for full
    cross-platform driver switching.
    """
    return pytest.mark.parametrize(
        "platform",
        [pytest.param(p, id=p) for p in platforms],
    )
