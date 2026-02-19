"""Login screen page object."""


from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class LoginPage(BasePage):
    # ── Locators ────────────────────────────────────────────────────────────
    # Replace the resource-id strings with the real IDs from your app.
    # Use Appium Inspector to find them: https://inspector.appiumpro.com

    _USERNAME_FIELD = (AppiumBy.ID, "com.example.myapp:id/username")
    _PASSWORD_FIELD = (AppiumBy.ID, "com.example.myapp:id/password")
    _LOGIN_BUTTON   = (AppiumBy.ID, "com.example.myapp:id/btn_login")
    _ERROR_MESSAGE  = (AppiumBy.ID, "com.example.myapp:id/error_message")
    _FORGOT_PASSWORD_LINK = (AppiumBy.ID, "com.example.myapp:id/forgot_password")

    # ── Actions ─────────────────────────────────────────────────────────────

    def login(self, username: str, password: str) -> None:
        """Fill credentials and submit the login form."""
        self.actions.type_text(self._USERNAME_FIELD, username)
        self.actions.type_text(self._PASSWORD_FIELD, password)
        self.actions.tap(self._LOGIN_BUTTON)

    def tap_forgot_password(self) -> None:
        self.actions.tap(self._FORGOT_PASSWORD_LINK)

    # ── Queries ─────────────────────────────────────────────────────────────

    def error_message(self) -> str:
        return self.actions.text(self._ERROR_MESSAGE)

    def is_error_visible(self) -> bool:
        return self.actions.exists(self._ERROR_MESSAGE)

    def is_loaded(self) -> bool:
        return self.actions.exists(self._USERNAME_FIELD)
