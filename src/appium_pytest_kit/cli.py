"""Command-line utilities for appium-pytest-kit."""


import argparse
from collections.abc import Sequence
from pathlib import Path

ENV_TEMPLATE = """# appium-pytest-kit starter configuration
# Copy this file to your project root and adjust values.

APP_PLATFORM=android
APP_APPIUM_URL=http://127.0.0.1:4723
APP_MANAGE_APPIUM_SERVER=false
APP_DEVICE_NAME=
APP_PLATFORM_VERSION=
APP_UDID=
APP_APP=
APP_APPIUM_BASE_PATH=/
APP_CAPABILITIES_JSON={}
APP_REPORTING_ENABLED=false
"""


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for `appium-pytest-kit-init`."""

    parser = argparse.ArgumentParser(description="Create a starter .env for appium-pytest-kit")
    parser.add_argument(
        "--path",
        default=".env",
        help="Output path for the generated env template (default: .env)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output file when it already exists",
    )
    return parser


def init_env_file(path: Path, *, force: bool = False) -> bool:
    """Create a starter env file. Returns True when written."""

    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ENV_TEMPLATE, encoding="utf-8")
    return True


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point used by `appium-pytest-kit-init`."""

    parser = build_parser()
    args = parser.parse_args(argv)

    output_path = Path(args.path)
    written = init_env_file(output_path, force=args.force)

    if written:
        print(f"Created {output_path}")
        return 0

    print(f"Skipped {output_path} (already exists). Use --force to overwrite.")
    return 0
