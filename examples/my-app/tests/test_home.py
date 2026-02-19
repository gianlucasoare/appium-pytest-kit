"""Home screen tests."""


import pytest


@pytest.mark.integration
class TestHomeScreen:

    def test_home_loads_after_login(self, logged_in_home):
        assert logged_in_home.is_loaded()

    def test_welcome_text_is_visible(self, logged_in_home):
        text = logged_in_home.welcome_text()
        assert text  # non-empty

    def test_search_bar_accepts_input(self, logged_in_home):
        logged_in_home.search("hello")
        # assert results appear — add your results locator check here


@pytest.mark.integration
class TestLogout:

    def test_logout_returns_to_login(self, logged_in_home, login_page):
        logged_in_home.logout()
        assert login_page.is_loaded()
