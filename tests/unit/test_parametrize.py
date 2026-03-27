"""Tests for data-driven test helpers (parametrize module)."""

import json

import pytest

from appium_pytest_kit.parametrize import cross_platform, from_file, load_test_data


class TestLoadTestData:
    """Tests for load_test_data()."""

    def test_loads_json_file(self, tmp_path):
        data = [{"name": "case1", "value": 1}, {"name": "case2", "value": 2}]
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        result = load_test_data(path)

        assert result == data
        assert len(result) == 2

    def test_loads_yaml_file(self, tmp_path):
        pytest.importorskip("yaml")
        content = "- name: case1\n  value: 1\n- name: case2\n  value: 2\n"
        path = tmp_path / "cases.yaml"
        path.write_text(content)

        result = load_test_data(path)

        assert len(result) == 2
        assert result[0]["name"] == "case1"

    def test_loads_yml_extension(self, tmp_path):
        pytest.importorskip("yaml")
        content = "- name: only\n"
        path = tmp_path / "cases.yml"
        path.write_text(content)

        result = load_test_data(path)

        assert len(result) == 1

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="not found"):
            load_test_data(tmp_path / "missing.json")

    def test_raises_on_unsupported_format(self, tmp_path):
        path = tmp_path / "cases.txt"
        path.write_text("hello")

        with pytest.raises(ValueError, match="Unsupported"):
            load_test_data(path)

    def test_platform_filter(self, tmp_path):
        data = {
            "android": [{"name": "a1"}],
            "ios": [{"name": "i1"}, {"name": "i2"}],
        }
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        result = load_test_data(path, platform="android")

        assert len(result) == 1
        assert result[0]["name"] == "a1"

    def test_platform_filter_empty(self, tmp_path):
        data = {"android": [{"name": "a1"}]}
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        result = load_test_data(path, platform="ios")

        assert result == []

    def test_platform_filter_requires_mapping(self, tmp_path):
        data = [{"name": "flat"}]
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        with pytest.raises(ValueError, match="mapping with platform keys"):
            load_test_data(path, platform="android")

    def test_key_filter(self, tmp_path):
        data = {"smoke": [{"name": "s1"}], "regression": [{"name": "r1"}, {"name": "r2"}]}
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        result = load_test_data(path, key="regression")

        assert len(result) == 2

    def test_key_filter_requires_mapping(self, tmp_path):
        data = [{"name": "flat"}]
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        with pytest.raises(ValueError, match="mapping with key"):
            load_test_data(path, key="smoke")

    def test_raises_if_result_not_list(self, tmp_path):
        data = "just a string"
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        with pytest.raises(ValueError, match="Expected a list"):
            load_test_data(path)

    def test_yaml_import_error_message(self, tmp_path, monkeypatch):
        path = tmp_path / "cases.yaml"
        path.write_text("- name: test\n")

        import appium_pytest_kit.parametrize as mod

        def _load_yaml_no_pyyaml(p):
            raise ImportError(
                f"PyYAML is required to load {p}. "
                "Install it with: pip install appium-pytest-kit[yaml]"
            )

        monkeypatch.setattr(mod, "_load_yaml", _load_yaml_no_pyyaml)

        with pytest.raises(ImportError, match="PyYAML is required"):
            load_test_data(path)


class TestFromFile:
    """Tests for the @from_file decorator."""

    def test_returns_parametrize_marker(self, tmp_path):
        data = [{"name": "case1", "x": 1}, {"name": "case2", "x": 2}]
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        decorator = from_file(str(path))

        assert hasattr(decorator, "args")
        assert decorator.args[0] == "case"

    def test_custom_id_field(self, tmp_path):
        data = [{"scenario": "login", "x": 1}]
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        decorator = from_file(str(path), id_field="scenario")

        param = decorator.args[1][0]
        assert param.id == "login"

    def test_numeric_fallback_id(self, tmp_path):
        data = [{"x": 1}]
        path = tmp_path / "cases.json"
        path.write_text(json.dumps(data))

        decorator = from_file(str(path))

        param = decorator.args[1][0]
        assert param.id == "0"


class TestCrossPlatform:
    """Tests for the @cross_platform decorator."""

    def test_default_platforms(self):
        decorator = cross_platform()

        assert decorator.args[0] == "platform"
        ids = [p.id for p in decorator.args[1]]
        assert ids == ["android", "ios"]

    def test_custom_platforms(self):
        decorator = cross_platform(platforms=("android", "ios", "web"))

        ids = [p.id for p in decorator.args[1]]
        assert ids == ["android", "ios", "web"]
