"""Tests for the soft assertions module."""

import pytest

from appium_pytest_kit.soft_assertions import (
    AssertionFailure,
    SoftAssert,
    SoftAssertionError,
    soft_assertions,
)


class TestSoftAssertBasic:
    """Core SoftAssert behavior."""

    def test_no_failures_does_not_raise(self) -> None:
        sa = SoftAssert()
        sa.check(True, "this passes")
        sa.assert_all()  # should not raise

    def test_single_failure_raises(self) -> None:
        sa = SoftAssert()
        sa.check(False, "expected X")
        with pytest.raises(SoftAssertionError, match="1 soft assertion"):
            sa.assert_all()

    def test_multiple_failures_collected(self) -> None:
        sa = SoftAssert()
        sa.check(False, "fail 1")
        sa.check(False, "fail 2")
        sa.check(True, "pass")
        sa.check(False, "fail 3")

        with pytest.raises(SoftAssertionError) as exc_info:
            sa.assert_all()

        assert exc_info.value.failure_count == 3
        assert "3 soft assertion" in str(exc_info.value)
        assert "fail 1" in str(exc_info.value)
        assert "fail 2" in str(exc_info.value)
        assert "fail 3" in str(exc_info.value)

    def test_assert_all_resets_after_raise(self) -> None:
        sa = SoftAssert()
        sa.check(False, "will be cleared")
        with pytest.raises(SoftAssertionError):
            sa.assert_all()
        # second call should not raise (failures cleared)
        sa.assert_all()

    def test_reset_clears_without_raising(self) -> None:
        sa = SoftAssert()
        sa.check(False, "recorded")
        assert sa.failed is True
        sa.reset()
        assert sa.failed is False
        sa.assert_all()  # should not raise


class TestSoftAssertShorthands:
    """Shorthand methods (check_equal, check_true, etc.)."""

    def test_check_equal_pass(self) -> None:
        sa = SoftAssert()
        sa.check_equal(42, 42, label="answer")
        assert sa.failed is False

    def test_check_equal_fail(self) -> None:
        sa = SoftAssert()
        sa.check_equal("actual", "expected", label="field")
        assert sa.failed is True
        assert sa.failures[0].expected == "expected"
        assert sa.failures[0].actual == "actual"

    def test_check_true_pass(self) -> None:
        sa = SoftAssert()
        sa.check_true(1, label="truthy")
        assert sa.failed is False

    def test_check_true_fail(self) -> None:
        sa = SoftAssert()
        sa.check_true(0, "zero is not truthy", label="zero")
        assert sa.failures[0].actual == 0

    def test_check_false_pass(self) -> None:
        sa = SoftAssert()
        sa.check_false(0, label="falsy")
        assert sa.failed is False

    def test_check_false_fail(self) -> None:
        sa = SoftAssert()
        sa.check_false(1, label="one")
        assert sa.failed is True

    def test_check_in_pass(self) -> None:
        sa = SoftAssert()
        sa.check_in("a", ["a", "b", "c"], label="member")
        assert sa.failed is False

    def test_check_in_fail(self) -> None:
        sa = SoftAssert()
        sa.check_in("x", ["a", "b"], label="missing")
        assert sa.failed is True

    def test_check_not_none_pass(self) -> None:
        sa = SoftAssert()
        sa.check_not_none("value", label="exists")
        assert sa.failed is False

    def test_check_not_none_fail(self) -> None:
        sa = SoftAssert()
        sa.check_not_none(None, label="missing")
        assert sa.failed is True

    def test_check_gt_pass(self) -> None:
        sa = SoftAssert()
        sa.check_gt(10, 5, label="greater")
        assert sa.failed is False

    def test_check_gt_fail(self) -> None:
        sa = SoftAssert()
        sa.check_gt(3, 5, label="not_greater")
        assert sa.failed is True

    def test_check_lt_pass(self) -> None:
        sa = SoftAssert()
        sa.check_lt(3, 5, label="less")
        assert sa.failed is False

    def test_check_lt_fail(self) -> None:
        sa = SoftAssert()
        sa.check_lt(10, 5, label="not_less")
        assert sa.failed is True

    def test_check_contains_pass(self) -> None:
        sa = SoftAssert()
        sa.check_contains("Hello World", "World", label="greeting")
        assert sa.failed is False

    def test_check_contains_fail(self) -> None:
        sa = SoftAssert()
        sa.check_contains("Hello World", "Missing", label="nope")
        assert sa.failed is True


class TestSoftAssertInspection:
    """Inspection properties and failure records."""

    def test_failure_count(self) -> None:
        sa = SoftAssert()
        assert sa.failure_count == 0
        sa.check(False, "one")
        sa.check(False, "two")
        assert sa.failure_count == 2

    def test_failed_property(self) -> None:
        sa = SoftAssert()
        assert sa.failed is False
        sa.check(False, "oops")
        assert sa.failed is True

    def test_failures_returns_copy(self) -> None:
        sa = SoftAssert()
        sa.check(False, "recorded")
        copy1 = sa.failures
        copy2 = sa.failures
        assert copy1 == copy2
        assert copy1 is not copy2  # must be a copy

    def test_failure_record_has_all_fields(self) -> None:
        sa = SoftAssert()
        sa.check(False, "msg", label="lbl", expected=42, actual=0)
        f = sa.failures[0]
        assert f.message == "msg"
        assert f.label == "lbl"
        assert f.expected == 42
        assert f.actual == 0


class TestSoftAssertionError:
    """Error class behavior."""

    def test_inherits_from_base_error(self) -> None:
        from appium_pytest_kit.errors import AppiumPytestKitError

        assert issubclass(SoftAssertionError, AppiumPytestKitError)

    def test_error_message_formatting(self) -> None:
        failures = [
            AssertionFailure(message="title wrong", label="title", expected="Home", actual="Login"),
            AssertionFailure(message="count off", label=None, expected=5, actual=3),
        ]
        exc = SoftAssertionError(failures)
        msg = str(exc)
        assert "2 soft assertion(s) failed" in msg
        assert "(title)" in msg
        assert "title wrong" in msg
        assert "expected='Home'" in msg
        assert "actual='Login'" in msg
        assert "count off" in msg

    def test_failures_attribute(self) -> None:
        failures = [AssertionFailure(message="x")]
        exc = SoftAssertionError(failures)
        assert len(exc.failures) == 1
        assert exc.failures[0].message == "x"


class TestSoftAssertionsContextManager:
    """The ``soft_assertions()`` context manager."""

    def test_context_raises_on_failure(self) -> None:
        with pytest.raises(SoftAssertionError, match="2 soft"):
            with soft_assertions() as sa:
                sa.check(False, "a")
                sa.check(False, "b")

    def test_context_does_not_raise_on_success(self) -> None:
        with soft_assertions() as sa:
            sa.check(True, "ok")
            sa.check_equal(1, 1)

    def test_context_yields_soft_assert(self) -> None:
        with soft_assertions() as sa:
            assert isinstance(sa, SoftAssert)

    def test_real_world_form_validation(self) -> None:
        """Simulates a real form validation scenario."""
        title = "Login"
        username_visible = True
        password_visible = True
        submit_enabled = False
        error_text = ""

        with pytest.raises(SoftAssertionError) as exc_info:
            with soft_assertions() as sa:
                sa.check_equal(title, "Home", label="page_title")
                sa.check_true(username_visible, label="username_field")
                sa.check_true(password_visible, label="password_field")
                sa.check_true(submit_enabled, label="submit_button")
                sa.check_equal(error_text, "", label="error_message")

        # Only 2 should fail: title and submit_enabled
        assert exc_info.value.failure_count == 2
