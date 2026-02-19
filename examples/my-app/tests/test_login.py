"""Login screen tests."""


import pytest
from conftest import TEST_PASSWORD, TEST_USERNAME


@pytest.mark.integration
class TestLoginSuccess:

    def test_valid_credentials_open_home(self, login_page, home_page):
        login_page.login(TEST_USERNAME, TEST_PASSWORD)
        assert home_page.is_loaded()

    def test_welcome_text_contains_username(self, logged_in_home):
        assert TEST_USERNAME.split("@")[0] in logged_in_home.welcome_text()


@pytest.mark.integration
class TestLoginFailure:

    def test_wrong_password_shows_error(self, login_page):
        login_page.login(TEST_USERNAME, "wrongpassword")
        assert login_page.is_error_visible()

    def test_error_message_content(self, login_page):
        login_page.login(TEST_USERNAME, "wrongpassword")
        assert "Invalid" in login_page.error_message()

    def test_empty_username_shows_error(self, login_page):
        login_page.login("", TEST_PASSWORD)
        assert login_page.is_error_visible()

    def test_empty_password_shows_error(self, login_page):
        login_page.login(TEST_USERNAME, "")
        assert login_page.is_error_visible()


@pytest.mark.integration
class TestLoginNavigation:

    def test_forgot_password_link_is_tappable(self, login_page):
        assert login_page.is_loaded()
        login_page.tap_forgot_password()
        # assert next screen loads — replace with your forgot-password page check
