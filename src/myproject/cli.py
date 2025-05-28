"""Command-line interface for myproject."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MyProject CLI — a template command-line entry point."
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Show the current version"
    )
    args = parser.parse_args()

    if args.version:
        # Lazy import to avoid circular import at top level
        from myproject import __version__

        print(f"MyProject version {__version__}")
    else:
        print("Hello from MyProject CLI!")
