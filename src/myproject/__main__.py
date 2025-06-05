"""
CLI entry point for `python -m myproject`.

This module allows invoking the CLI without installing the package,
by executing:

    python -m myproject [arguments]

Note:
    When the package is installed, a `myproject` executable is also
    generated via the `pyproject.toml` section:

        [project.scripts]
        myproject = "myproject.__main__:main"

    This lets users run the CLI simply as:

        myproject [arguments]
"""

from myproject.cli.cli_main import main

if __name__ == "__main__":
    main()
