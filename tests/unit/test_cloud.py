"""Tests for the device farm cloud provider module."""

import pytest

from appium_pytest_kit.cloud import (
    CloudConfig,
    apply_cloud_config,
    build_cloud_config,
)
from appium_pytest_kit.errors import ConfigurationError


class TestBrowserStack:
    """BrowserStack adapter tests."""

    def test_builds_server_url_with_credentials(self, monkeypatch) -> None:
        monkeypatch.setenv("BROWSERSTACK_USERNAME", "testuser")
        monkeypatch.setenv("BROWSERSTACK_ACCESS_KEY", "testkey123")

        config = build_cloud_config("browserstack")

        assert config.provider == "browserstack"
        assert "testuser:testkey123" in config.server_url
        assert "hub-cloud.browserstack.com" in config.server_url

    def test_includes_project_and_build(self, monkeypatch) -> None:
        monkeypatch.setenv("BROWSERSTACK_USERNAME", "user")
        monkeypatch.setenv("BROWSERSTACK_ACCESS_KEY", "key")

        config = build_cloud_config(
            "browserstack",
            project="My App",
            build="CI #42",
            name="Login Test",
            device="Google Pixel 7",
            os_version="13.0",
        )

        opts = config.capabilities["bstack:options"]
        assert opts["projectName"] == "My App"
        assert opts["buildName"] == "CI #42"
        assert opts["sessionName"] == "Login Test"
        assert opts["deviceName"] == "Google Pixel 7"
        assert opts["osVersion"] == "13.0"

    def test_uses_browserstack_app_env(self, monkeypatch) -> None:
        monkeypatch.setenv("BROWSERSTACK_USERNAME", "user")
        monkeypatch.setenv("BROWSERSTACK_ACCESS_KEY", "key")
        monkeypatch.setenv("BROWSERSTACK_APP", "bs://abc123")

        config = build_cloud_config("browserstack")

        assert config.capabilities["bstack:options"]["appUrl"] == "bs://abc123"

    def test_app_argument_overrides_env(self, monkeypatch) -> None:
        monkeypatch.setenv("BROWSERSTACK_USERNAME", "user")
        monkeypatch.setenv("BROWSERSTACK_ACCESS_KEY", "key")
        monkeypatch.setenv("BROWSERSTACK_APP", "bs://env_value")

        config = build_cloud_config("browserstack", app="bs://arg_value")

        assert config.capabilities["bstack:options"]["appUrl"] == "bs://arg_value"

    def test_missing_username_raises(self, monkeypatch) -> None:
        monkeypatch.delenv("BROWSERSTACK_USERNAME", raising=False)
        monkeypatch.setenv("BROWSERSTACK_ACCESS_KEY", "key")

        with pytest.raises(ConfigurationError, match="BROWSERSTACK_USERNAME"):
            build_cloud_config("browserstack")

    def test_missing_access_key_raises(self, monkeypatch) -> None:
        monkeypatch.setenv("BROWSERSTACK_USERNAME", "user")
        monkeypatch.delenv("BROWSERSTACK_ACCESS_KEY", raising=False)

        with pytest.raises(ConfigurationError, match="BROWSERSTACK_ACCESS_KEY"):
            build_cloud_config("browserstack")

    def test_extra_capabilities_merged(self, monkeypatch) -> None:
        monkeypatch.setenv("BROWSERSTACK_USERNAME", "user")
        monkeypatch.setenv("BROWSERSTACK_ACCESS_KEY", "key")

        config = build_cloud_config(
            "browserstack",
            extra={"appium:autoGrantPermissions": True},
        )

        assert config.capabilities["appium:autoGrantPermissions"] is True


class TestSauceLabs:
    """Sauce Labs adapter tests."""

    def test_builds_server_url(self, monkeypatch) -> None:
        monkeypatch.setenv("SAUCE_USERNAME", "sauceuser")
        monkeypatch.setenv("SAUCE_ACCESS_KEY", "saucekey")

        config = build_cloud_config("saucelabs")

        assert config.provider == "saucelabs"
        assert "sauceuser:saucekey" in config.server_url
        assert "saucelabs.com" in config.server_url

    def test_custom_data_center(self, monkeypatch) -> None:
        monkeypatch.setenv("SAUCE_USERNAME", "user")
        monkeypatch.setenv("SAUCE_ACCESS_KEY", "key")

        config = build_cloud_config("saucelabs", data_center="eu-central-1")

        assert "eu-central-1" in config.server_url

    def test_sauce_alias(self, monkeypatch) -> None:
        monkeypatch.setenv("SAUCE_USERNAME", "user")
        monkeypatch.setenv("SAUCE_ACCESS_KEY", "key")

        config = build_cloud_config("sauce")

        assert config.provider == "saucelabs"

    def test_device_and_version_in_capabilities(self, monkeypatch) -> None:
        monkeypatch.setenv("SAUCE_USERNAME", "user")
        monkeypatch.setenv("SAUCE_ACCESS_KEY", "key")

        config = build_cloud_config(
            "saucelabs",
            device="iPhone 14",
            platform_version="16.0",
            build="CI #99",
            name="Smoke",
        )

        assert config.capabilities["appium:deviceName"] == "iPhone 14"
        assert config.capabilities["appium:platformVersion"] == "16.0"
        assert config.capabilities["sauce:options"]["build"] == "CI #99"

    def test_sauce_app_env_fallback(self, monkeypatch) -> None:
        monkeypatch.setenv("SAUCE_USERNAME", "user")
        monkeypatch.setenv("SAUCE_ACCESS_KEY", "key")
        monkeypatch.setenv("SAUCE_APP", "storage:filename=app.apk")

        config = build_cloud_config("saucelabs")

        assert config.capabilities["sauce:options"]["app"] == "storage:filename=app.apk"

    def test_missing_credentials_raises(self, monkeypatch) -> None:
        monkeypatch.delenv("SAUCE_USERNAME", raising=False)
        monkeypatch.delenv("SAUCE_ACCESS_KEY", raising=False)

        with pytest.raises(ConfigurationError, match="SAUCE_USERNAME"):
            build_cloud_config("saucelabs")


class TestAWSDeviceFarm:
    """AWS Device Farm adapter tests."""

    def test_builds_with_arn(self, monkeypatch) -> None:
        monkeypatch.setenv("AWS_DEVICE_FARM_ARN", "arn:aws:devicefarm:us-west-2:123:project:abc")
        monkeypatch.setenv("AWS_DEFAULT_REGION", "us-west-2")

        config = build_cloud_config("aws")

        assert config.provider == "aws"
        assert "devicefarm.us-west-2.amazonaws.com" in config.server_url
        assert "arn:aws:devicefarm" in config.capabilities["appium:deviceFarm:projectArn"]

    def test_arn_argument_overrides_env(self, monkeypatch) -> None:
        monkeypatch.setenv("AWS_DEVICE_FARM_ARN", "arn:env")

        config = build_cloud_config("aws", project_arn="arn:arg")

        assert config.capabilities["appium:deviceFarm:projectArn"] == "arn:arg"

    def test_missing_arn_raises(self, monkeypatch) -> None:
        monkeypatch.delenv("AWS_DEVICE_FARM_ARN", raising=False)

        with pytest.raises(ConfigurationError, match="AWS_DEVICE_FARM_ARN"):
            build_cloud_config("aws")

    def test_alias_aws_device_farm(self, monkeypatch) -> None:
        monkeypatch.setenv("AWS_DEVICE_FARM_ARN", "arn:aws:test")

        config = build_cloud_config("aws_device_farm")

        assert config.provider == "aws"


class TestBuildCloudConfig:
    """Factory function edge cases."""

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ConfigurationError, match="Unknown cloud provider"):
            build_cloud_config("unknown_provider")

    def test_case_insensitive_provider(self, monkeypatch) -> None:
        monkeypatch.setenv("BROWSERSTACK_USERNAME", "user")
        monkeypatch.setenv("BROWSERSTACK_ACCESS_KEY", "key")

        config = build_cloud_config("BrowserStack")

        assert config.provider == "browserstack"


class TestApplyCloudConfig:
    """Merging cloud capabilities into existing caps."""

    def test_merges_capabilities(self) -> None:
        existing = {"platformName": "android", "deviceName": "Pixel 7"}
        cloud = CloudConfig(
            provider="browserstack",
            server_url="https://hub.example.com",
            capabilities={"bstack:options": {"buildName": "test"}},
        )

        merged = apply_cloud_config(existing, cloud)

        assert merged["platformName"] == "android"
        assert merged["deviceName"] == "Pixel 7"
        assert merged["bstack:options"]["buildName"] == "test"

    def test_does_not_mutate_input(self) -> None:
        existing = {"platformName": "android"}
        cloud = CloudConfig(
            provider="saucelabs",
            server_url="https://hub.example.com",
            capabilities={"sauce:options": {}},
        )

        merged = apply_cloud_config(existing, cloud)

        assert "sauce:options" not in existing
        assert "sauce:options" in merged
