"""Tests for the --framework scaffold CLI flag."""

from pathlib import Path

from appium_pytest_kit.cli import main, scaffold_framework


class TestScaffoldFramework:
    def test_creates_expected_files(self, tmp_path: Path) -> None:
        created = scaffold_framework(tmp_path)
        assert len(created) > 0

        paths = {Path(p).relative_to(tmp_path).as_posix() for p in created}
        assert "data/devices.yaml" in paths
        assert "api/client.py" in paths
        assert "pages/base_page.py" in paths
        assert "conftest.py" in paths
        assert "pytest.ini" in paths
        assert "tests/api/test_health.py" in paths
        assert "tests/android/test_smoke.py" in paths
        assert "tests/ios/test_smoke.py" in paths

    def test_devices_yaml_has_devices_key(self, tmp_path: Path) -> None:
        scaffold_framework(tmp_path)
        content = (tmp_path / "data/devices.yaml").read_text(encoding="utf-8")
        assert "devices:" in content

    def test_smoke_test_is_valid_python(self, tmp_path: Path) -> None:
        scaffold_framework(tmp_path)
        test_file = tmp_path / "tests/android/test_smoke.py"
        # Compile check — raises SyntaxError if broken
        compile(test_file.read_text(encoding="utf-8"), str(test_file), "exec")

    def test_api_test_is_valid_python(self, tmp_path: Path) -> None:
        scaffold_framework(tmp_path)
        test_file = tmp_path / "tests/api/test_health.py"
        compile(test_file.read_text(encoding="utf-8"), str(test_file), "exec")

    def test_force_overwrites_existing(self, tmp_path: Path) -> None:
        (tmp_path / "pytest.ini").mkdir()  # make it a dir so first run skips it
        # First run: dir exists but not a file, scaffold_framework won't overwrite
        scaffold_framework(tmp_path, force=False)
        # Remove the blocking dir
        (tmp_path / "pytest.ini").rmdir()
        # Second run with force creates pytest.ini
        scaffold_framework(tmp_path, force=True)
        assert (tmp_path / "pytest.ini").is_file()

    def test_no_force_skips_existing_files(self, tmp_path: Path) -> None:
        (tmp_path / "conftest.py").write_text("# existing\n", encoding="utf-8")
        scaffold_framework(tmp_path, force=False)
        # Existing file must not be overwritten
        assert "# existing" in (tmp_path / "conftest.py").read_text(encoding="utf-8")

    def test_force_overwrites_existing_files(self, tmp_path: Path) -> None:
        (tmp_path / "conftest.py").write_text("# old\n", encoding="utf-8")
        scaffold_framework(tmp_path, force=True)
        assert "# old" not in (tmp_path / "conftest.py").read_text(encoding="utf-8")


class TestMainFrameworkFlag:
    def test_main_with_framework_flag(self, tmp_path: Path, capsys) -> None:
        code = main(["--framework", "--root", str(tmp_path)])
        assert code == 0
        captured = capsys.readouterr()
        assert "Scaffolded" in captured.out

    def test_main_without_framework_creates_env(self, tmp_path: Path, capsys) -> None:
        env_path = tmp_path / ".env"
        code = main(["--path", str(env_path)])
        assert code == 0
        assert env_path.exists()
