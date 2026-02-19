"""Profile screen tests."""


import pytest
from conftest import TEST_USERNAME


@pytest.mark.integration
class TestProfileScreen:

    def test_profile_shows_username(self, logged_in_profile):
        assert TEST_USERNAME in logged_in_profile.username()

    def test_profile_shows_email(self, logged_in_profile):
        email = logged_in_profile.email()
        assert "@" in email

    def test_profile_loads(self, logged_in_profile):
        assert logged_in_profile.is_loaded()


@pytest.mark.integration
class TestProfileEdit:

    def test_edit_and_save_display_name(self, logged_in_profile):
        logged_in_profile.tap_edit()
        logged_in_profile.update_display_name("New Name")
        logged_in_profile.save()
        # assert the change persisted — add your verification locator here

    def test_back_button_returns_to_home(self, logged_in_profile, home_page):
        logged_in_profile.go_back()
        assert home_page.is_loaded()
