"""Home screen page object."""


from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class HomePage(BasePage):
    # ── Locators ────────────────────────────────────────────────────────────

    _WELCOME_TEXT  = (AppiumBy.ID, "com.example.myapp:id/welcome_text")
    _PROFILE_ICON  = (AppiumBy.ID, "com.example.myapp:id/icon_profile")
    _SEARCH_BAR    = (AppiumBy.ID, "com.example.myapp:id/search_bar")
    _LOGOUT_BUTTON = (AppiumBy.ID, "com.example.myapp:id/btn_logout")

    # ── Actions ─────────────────────────────────────────────────────────────

    def tap_profile(self) -> None:
        self.actions.tap(self._PROFILE_ICON)

    def search(self, query: str) -> None:
        self.actions.type_text(self._SEARCH_BAR, query)

    def logout(self) -> None:
        self.actions.tap(self._LOGOUT_BUTTON)

    # ── Queries ─────────────────────────────────────────────────────────────

    def welcome_text(self) -> str:
        return self.actions.text(self._WELCOME_TEXT)

    def is_loaded(self) -> bool:
        return self.actions.exists(self._WELCOME_TEXT)
