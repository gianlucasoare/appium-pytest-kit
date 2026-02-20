"""Profile flow — orchestrates navigation and edits on the profile screen."""


from pages.home_page import HomePage
from pages.profile_page import ProfilePage

from flows.base_flow import BaseFlow


class ProfileFlow(BaseFlow):
    """Coordinates HomePage and ProfilePage to express profile journeys."""

    # ── Private page factories ───────────────────────────────────────────────

    def _home_page(self) -> HomePage:
        return HomePage(self.driver, self.waiter, self.actions)

    def _profile_page(self) -> ProfilePage:
        return ProfilePage(self.driver, self.waiter, self.actions)

    # ── Flow steps ───────────────────────────────────────────────────────────

    def open_profile(self) -> ProfilePage:
        """Tap the profile icon on home and confirm the profile screen loads."""
        self._home_page().tap_profile()
        profile = self._profile_page()
        assert profile.is_loaded(), "Profile page did not load"
        return profile

    def edit_display_name(self, new_name: str) -> ProfilePage:
        """Open profile, update the display name, save, and return the page."""
        profile = self.open_profile()
        profile.tap_edit()
        profile.update_display_name(new_name)
        profile.save()
        return profile

    def get_profile_details(self) -> dict[str, str]:
        """Open profile and return username + email as a dict."""
        profile = self.open_profile()
        return {
            "username": profile.username(),
            "email": profile.email(),
        }
