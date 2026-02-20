"""Authentication flow — orchestrates login and logout across pages."""


from pages.home_page import HomePage
from pages.login_page import LoginPage

from flows.base_flow import BaseFlow


class AuthFlow(BaseFlow):
    """Coordinates LoginPage and HomePage to express auth journeys."""

    # ── Private page factories ───────────────────────────────────────────────
    # Each method returns a fresh page object bound to the current driver.

    def _login_page(self) -> LoginPage:
        return LoginPage(self.driver, self.waiter, self.actions)

    def _home_page(self) -> HomePage:
        return HomePage(self.driver, self.waiter, self.actions)

    # ── Flow steps ───────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> HomePage:
        """Fill credentials, submit the form, and confirm home screen loads."""
        self._login_page().login(username, password)
        home = self._home_page()
        assert home.is_loaded(), "Home page did not load after login"
        return home

    def logout(self) -> LoginPage:
        """Tap logout on the home screen and confirm the login screen appears."""
        self._home_page().logout()
        login = self._login_page()
        assert login.is_loaded(), "Login page did not appear after logout"
        return login

    def login_then_logout(self, username: str, password: str) -> LoginPage:
        """Full round-trip: log in then immediately log out."""
        self.login(username, password)
        return self.logout()
