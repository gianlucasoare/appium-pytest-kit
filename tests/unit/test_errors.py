"""Tests for the enriched exception hierarchy."""


from appium_pytest_kit.errors import (
    ActionError,
    ApiRequestError,
    ConfigurationError,
    DeviceResolutionError,
    DriverCreationError,
    LaunchValidationError,
    WaitTimeoutError,
)


def test_wait_timeout_error_basic_message() -> None:
    exc = WaitTimeoutError("Element missing")
    assert "Element missing" in str(exc)
    assert exc.locator is None
    assert exc.timeout is None


def test_wait_timeout_error_with_locator() -> None:
    locator = ("accessibility id", "submit_button")
    exc = WaitTimeoutError("Not found", locator=locator)
    assert "accessibility id" in str(exc)
    assert "submit_button" in str(exc)
    assert exc.locator == locator


def test_wait_timeout_error_with_timeout() -> None:
    exc = WaitTimeoutError("Timed out", timeout=5.0)
    assert "5.0s" in str(exc)
    assert exc.timeout == 5.0


def test_wait_timeout_error_with_all_context() -> None:
    locator = ("id", "foo")
    exc = WaitTimeoutError("Bad", locator=locator, timeout=10.0)
    msg = str(exc)
    assert "Bad" in msg
    assert "id" in msg
    assert "foo" in msg
    assert "10.0s" in msg


def test_action_error_basic_message() -> None:
    exc = ActionError("Tap failed")
    assert "Tap failed" in str(exc)
    assert exc.locator is None
    assert exc.action is None


def test_action_error_with_locator() -> None:
    locator = ("xpath", "//button")
    exc = ActionError("Failed", locator=locator)
    assert "xpath" in str(exc)
    assert "//button" in str(exc)
    assert exc.locator == locator


def test_action_error_with_action_prefix() -> None:
    exc = ActionError("Click fail", action="tap")
    assert str(exc).startswith("[tap]")


def test_action_error_with_full_context() -> None:
    locator = ("id", "btn")
    exc = ActionError("Failed", locator=locator, action="swipe")
    msg = str(exc)
    assert "[swipe]" in msg
    assert "btn" in msg


def test_new_error_classes_are_base_subclass() -> None:
    from appium_pytest_kit.errors import AppiumPytestKitError

    assert issubclass(DeviceResolutionError, AppiumPytestKitError)
    assert issubclass(LaunchValidationError, AppiumPytestKitError)
    assert issubclass(ConfigurationError, AppiumPytestKitError)
    assert issubclass(DriverCreationError, AppiumPytestKitError)
    assert issubclass(ApiRequestError, AppiumPytestKitError)


def test_api_request_error_with_context() -> None:
    exc = ApiRequestError(
        "bad gateway",
        method="get",
        url="https://example.test/api",
        status_code=502,
    )
    assert exc.method == "get"
    assert exc.url == "https://example.test/api"
    assert exc.status_code == 502
    assert "GET" in str(exc)
    assert "status=502" in str(exc)
