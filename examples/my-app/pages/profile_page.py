"""Profile screen page object."""


from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class ProfilePage(BasePage):
    # ── Locators ────────────────────────────────────────────────────────────

    _USERNAME_LABEL   = (AppiumBy.ID, "com.example.myapp:id/profile_username")
    _EMAIL_LABEL      = (AppiumBy.ID, "com.example.myapp:id/profile_email")
    _EDIT_BUTTON      = (AppiumBy.ID, "com.example.myapp:id/btn_edit_profile")
    _SAVE_BUTTON      = (AppiumBy.ID, "com.example.myapp:id/btn_save_profile")
    _DISPLAY_NAME     = (AppiumBy.ID, "com.example.myapp:id/display_name")
    _BACK_BUTTON      = (AppiumBy.ACCESSIBILITY_ID, "Navigate up")

    # ── Actions ─────────────────────────────────────────────────────────────

    def tap_edit(self) -> None:
        self.actions.tap(self._EDIT_BUTTON)

    def update_display_name(self, name: str) -> None:
        self.actions.type_text(self._DISPLAY_NAME, name)

    def save(self) -> None:
        self.actions.tap(self._SAVE_BUTTON)

    def go_back(self) -> None:
        self.actions.tap(self._BACK_BUTTON)

    # ── Queries ─────────────────────────────────────────────────────────────

    def username(self) -> str:
        return self.actions.text(self._USERNAME_LABEL)

    def email(self) -> str:
        return self.actions.text(self._EMAIL_LABEL)

    def is_loaded(self) -> bool:
        return self.actions.exists(self._USERNAME_LABEL)
