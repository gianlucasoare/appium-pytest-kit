
import pytest


def test_settings_fixture_is_available(settings) -> None:
    assert settings.platform in {"android", "ios"}
    assert settings.appium_url.startswith("http")


@pytest.mark.integration
def test_driver_fixture_can_start_session(driver) -> None:
    assert driver.session_id is not None
