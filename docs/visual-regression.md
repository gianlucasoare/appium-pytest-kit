# Visual regression testing

appium-pytest-kit provides screenshot comparison with baseline management for detecting unintended UI changes.

## Quick start

```python
from appium_pytest_kit import assert_screenshot_match

def test_home_screen_looks_correct(driver, request):
    # Navigate to the screen you want to verify
    assert_screenshot_match(
        driver,
        test_id=request.node.nodeid,
        baselines_dir="baselines",
        artifacts_dir="artifacts",
        platform="android",
    )
```

On first run, this saves a baseline. On subsequent runs, it compares the current screenshot against the baseline and raises `VisualRegressionError` if the diff exceeds the threshold.

## How it works

1. **First run** — no baseline exists, so the screenshot is saved as the new baseline
2. **Subsequent runs** — the screenshot is compared pixel-by-pixel against the baseline
3. **Match** — diff ratio is within threshold, test passes
4. **Mismatch** — `VisualRegressionError` is raised with diff details

## Comparing screenshots

Use `compare_screenshots()` directly for manual comparison:

```python
from appium_pytest_kit import compare_screenshots

result = compare_screenshots(
    "artifacts/screenshots/actual.png",
    "baselines/expected.png",
    threshold=0.02,
    diff_output_path="artifacts/screenshots/diff.png",
)

print(f"Match: {result.match}")
print(f"Diff: {result.diff_ratio:.2%}")
print(f"Changed pixels: {result.diff_pixels}/{result.total_pixels}")
```

The diff image highlights changed pixels in red and unchanged pixels in greyscale.

## Baseline management

Use `BaselineManager` for programmatic baseline control:

```python
from appium_pytest_kit import BaselineManager

manager = BaselineManager("baselines")

# Check if a baseline exists
if manager.has_baseline("test_home", platform="android"):
    path = manager.baseline_path("test_home", platform="android")

# Save a new baseline
manager.save_baseline(
    "test_home",
    "artifacts/screenshots/home.png",
    platform="android",
    overwrite=True,
)
```

### Directory layout

Baselines are stored by platform:

```
baselines/
  android/
    tests__test_home__test_home_screen.png
    tests__test_login__test_login_form.png
  ios/
    tests__test_home__test_home_screen.png
    tests__test_login__test_login_form.png
```

## Threshold tuning

The `threshold` parameter controls how much pixel difference is tolerated:

| Threshold | Meaning |
|---|---|
| `0.0` | Exact match required (no tolerance) |
| `0.01` | 1% pixel difference allowed (default) |
| `0.05` | 5% — tolerates minor rendering differences |
| `0.10` | 10% — tolerates font/layout shifts across devices |

Choose a threshold based on your needs. Start with `0.01` and increase if you get false positives from anti-aliasing or device-specific rendering.

## Updating baselines

When the UI intentionally changes, update baselines:

```python
assert_screenshot_match(
    driver,
    test_id=request.node.nodeid,
    baselines_dir="baselines",
    artifacts_dir="artifacts",
    update_baselines=True,  # overwrites existing baseline
)
```

Or delete the baseline file and re-run the test — a new baseline is saved automatically.

## Error details

`VisualRegressionError` includes context for debugging:

```python
try:
    assert_screenshot_match(driver, ...)
except VisualRegressionError as e:
    print(e.diff_ratio)      # 0.0342
    print(e.threshold)       # 0.01
    print(e.baseline_path)   # baselines/android/test_home.png
    print(e.actual_path)     # artifacts/screenshots/visual/test_home.png
```

The diff image is saved alongside the actual screenshot in `artifacts/screenshots/visual/`.

## Requirements

Visual regression requires the `visual` extra:

```bash
pip install appium-pytest-kit[visual]
```

This installs [Pillow](https://python-pillow.org/) for image processing.

## Tips

- **Commit baselines to git** — they serve as the source of truth for visual appearance
- **Separate baselines by platform** — Android and iOS render differently
- **Use CI to catch regressions** — run visual tests in the main CI lane
- **Review diffs in PRs** — the diff image makes it easy to see what changed
- **Ignore dynamic content** — consider masking areas with timestamps or ads before comparison
