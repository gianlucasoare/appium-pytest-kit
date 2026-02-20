"""Tests using flows — multi-page orchestration objects.

Flows are the layer above page objects. Where a page object models a single
screen, a flow encodes a complete user journey that spans several screens.
Use flows when a test needs to perform a chain of actions across multiple
pages — this keeps the test body concise and the intent clear.
"""


import pytest
from conftest import TEST_PASSWORD, TEST_USERNAME

# ── Auth flow tests ──────────────────────────────────────────────────────────

@pytest.mark.integration
class TestAuthFlow:

    def test_valid_login_lands_on_home(self, auth_flow):
        """Logging in with correct credentials should open the home screen."""
        home = auth_flow.login(TEST_USERNAME, TEST_PASSWORD)
        assert home.is_loaded()

    def test_logout_returns_to_login_screen(self, logged_in, auth_flow):
        """After logging in, tapping logout should return to the login screen."""
        login = auth_flow.logout()
        assert login.is_loaded()

    def test_full_login_logout_roundtrip(self, auth_flow):
        """A complete log-in → log-out cycle should end on the login screen."""
        login = auth_flow.login_then_logout(TEST_USERNAME, TEST_PASSWORD)
        assert login.is_loaded()


# ── Profile flow tests ───────────────────────────────────────────────────────

@pytest.mark.integration
class TestProfileFlow:

    def test_open_profile_from_home(self, logged_in, profile_flow):
        """After login, tapping the profile icon should open the profile screen."""
        profile = profile_flow.open_profile()
        assert profile.is_loaded()

    def test_edit_display_name(self, logged_in, profile_flow):
        """Editing and saving a new display name should keep the profile loaded."""
        profile = profile_flow.edit_display_name("New Name")
        assert profile.is_loaded()

    def test_profile_details_contain_username_and_email(self, logged_in, profile_flow):
        """Profile details dict should include both username and email keys."""
        details = profile_flow.get_profile_details()
        assert "username" in details
        assert "email" in details
        assert details["username"]  # non-empty
        assert details["email"]     # non-empty
