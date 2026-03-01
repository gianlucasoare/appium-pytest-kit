# Commands

Canonical commands for this repository.

## Local Quality

```bash
ruff check .
python3 -m pytest -q
```

## Targeted Tests

```bash
python3 -m pytest -q tests/unit/test_pytest_plugin.py
python3 -m pytest -q tests/unit/test_actions_expanded2.py
```

## CI-Style Lanes (Local Approximation)

```bash
python3 -m pytest -q -m "not quarantine"
python3 -m pytest -q -m quarantine
python3 -m pytest -q -n 2 -m "not quarantine"
```

## Quality Gates

```bash
python3 scripts/check_flake_thresholds.py \
  --summary artifacts/appium-pytest-kit/flake-summary.json \
  --trend artifacts/appium-pytest-kit/flake-trend.json

python3 scripts/check_perf_thresholds.py \
  --summary artifacts/appium-pytest-kit/perf-summary.json \
  --trend artifacts/appium-pytest-kit/perf-trend.json
```

## Release

```bash
python3 -m build
python3 -m twine check dist/*
git tag vX.Y.Z
git push origin vX.Y.Z
```

## Changelog Automation

```bash
python3 scripts/update_changelog.py --version X.Y.Z
```
