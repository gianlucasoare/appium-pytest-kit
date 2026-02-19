"""Project-level fixtures and hook implementations.

This file is the main extension point for your test project.
Add page fixtures, shared helpers, and hook implementations here.
"""


import pytest
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.profile_page import ProfilePage

# ── Credentials ─────────────────────────────────────────────────────────────
# Keep test credentials in .env in real projects:
#   APP_CAPABILITIES_JSON={"testUsername": "user@example.com"}
# or use a dedicated secrets manager.

TEST_USERNAME = "testuser@example.com"
TEST_PASSWORD = "Test1234!"


# ── Page fixtures ────────────────────────────────────────────────────────────
# Each page fixture is function-scoped (one fresh instance per test).
# They receive driver/waiter/actions from appium-pytest-kit automatically.

@pytest.fixture
def login_page(driver, waiter, actions) -> LoginPage:
    return LoginPage(driver, waiter, actions)


@pytest.fixture
def home_page(driver, waiter, actions) -> HomePage:
    return HomePage(driver, waiter, actions)


@pytest.fixture
def profile_page(driver, waiter, actions) -> ProfilePage:
    return ProfilePage(driver, waiter, actions)


# ── Composed fixtures ────────────────────────────────────────────────────────
# Use these in tests that need a pre-authenticated state.

@pytest.fixture
def logged_in_home(login_page, home_page) -> HomePage:
    """Log in and return the home page ready for interaction."""
    login_page.login(TEST_USERNAME, TEST_PASSWORD)
    assert home_page.is_loaded(), "Home page did not load after login"
    return home_page


@pytest.fixture
def logged_in_profile(logged_in_home, home_page, profile_page) -> ProfilePage:
    """Log in, navigate to profile, and return the profile page."""
    home_page.tap_profile()
    assert profile_page.is_loaded(), "Profile page did not load"
    return profile_page


# ── Hook implementations ─────────────────────────────────────────────────────

def pytest_appium_pytest_kit_capabilities(capabilities, settings):
    """Add app-wide capabilities for every driver session."""
    if settings.platform == "android":
        return {
            "autoGrantPermissions": True,
        }
    if settings.platform == "ios":
        return {
            "autoAcceptAlerts": True,
        }


def pytest_appium_pytest_kit_driver_created(driver, settings):
    """Run immediately after each driver session is created."""
    driver.orientation = "PORTRAIT"
