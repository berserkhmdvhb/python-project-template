🧰 python-project-template

  

A modern, minimal, and reusable Python project template for building libraries, CLIs, or hybrid packages — designed with best practices, rich tooling, and robust environment-based behavior.


---

📚 Table of Contents

✨ Features

📦 Project Structure

📂 Structure

🧱 Architecture


🚀 Quickstart

🧑‍💼 Developer Guide

🔁 Continuous Integration

🌐 Publishing to PyPI

🎯 Goals

📄 License



---

✨ Features

📜 Modern pyproject.toml (PEP 621) for build and metadata

🧱 Clean hybrid architecture: CLI and importable core library

🔧 Environment-dependent behavior (DEV, UAT, PROD, TEST)

📁 Structured logging with:

Named log folders per environment (logs/ENV/)

Log rotation using RotatingFileHandler

Configurable limits via .env or system vars


📄 Robust environment management:

Automatic .env file detection

Manual override via CLI arg or DOTENV_PATH

Pytest-aware loading using PYTEST_CURRENT_TEST


🔍 Code quality tooling:

ruff, mypy, pytest, coverage

Pre-commit hooks to enforce standards


⚖️ Full CLI + core test coverage (100%)

💧 Developer-ready:

Makefile with rich commands

Modular conftest.py fixtures

GitHub Actions CI with multi-version Python


🌐 PyPI-ready: Includes .pypirc, test/publish targets



---

📦 Project Structure

📂 Structure

python-project-template/
├── .github/workflows/tests.yml        # GitHub CI pipeline
├── .pre-commit-config.yaml            # Pre-commit hooks
├── publish/
│   └── .pypirc.sample                 # Sample config for PyPI/TestPyPI
├── .env.sample                        # Sample environment config
├── LICENSE.txt
├── Makefile                           # Dev/test/publish automation
├── MANIFEST.in                        # sdist includes
├── pyproject.toml                     # Project metadata
├── README.md
├── src/
│   └── myproject/
│       ├── __init__.py                # Version metadata
│       ├── __main__.py                # Module entry point
│       ├── cli.py                     # Argument parsing
│       ├── cli_color_utils.py         # Colored terminal output
│       ├── cli_logger_utils.py        # Log rotation + setup
│       ├── constants.py               # Defaults, codes
│       ├── core.py                    # Main business logic
│       └── settings.py                # Env loading + config
└── tests/
    ├── conftest.py                    # Shared fixtures
    ├── test_cli.py                    # CLI integration
    ├── test_cli_env.py                # Env behavior
    ├── test_cli_logger_utils.py       # Logging
    ├── test_lib.py                    # Core logic
    ├── test_log.py                    # Logging config
    ├── test_settings.py               # Env parsing
    └── manual/demo.ipynb              # Notebook playground

🧱 Architecture

Separation of concerns for reliability, testing, and reuse:

1. Environment Configuration

settings.py: resolves .env files, honors override path, and detects test mode.

Automatically loads .env.override, .env, or .env.sample (fallback)


2. CLI Layer

cli.py: entry point parser and argument router

cli_color_utils.py: themed output helpers

cli_logger_utils.py: log formatting, rotation, and destination setup


3. Core Logic

core.py: stateless business logic (importable, testable)


4. Testing

CLI covered via subprocess and direct entry

Modular test files per domain

Full pytest and coverage support

.env.test simulation and temp .env overrides



---

🚀 Quickstart

📥 Installation

python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
make develop               # or: pip install -e .[dev]

💻 CLI Examples

myproject --version
myproject --query "hello"
python -m myproject --help


---

🧑‍💼 Developer Guide

🔧 Makefile Commands

Command	Description

make help	List available commands
make install	Install project in editable mode
make develop	Install with [dev] dependencies
make format	Format with Ruff
make lint	Lint and type check
make test	Run all tests
make test-fast	Only failed tests (if any)
make coverage	Show terminal coverage
make coverage-xml	Export XML coverage
make upload-coverage	Upload to Coveralls
make precommit	Install pre-commit
make precommit-run	Run hooks on all files
make build	Build wheel + sdist
make clean	Clean build/egg/dist artifacts
make publish-test	Push to TestPyPI
make publish	Push to PyPI


📋 Pre-commit

pre-commit install
pre-commit run --all-files


---

🔁 Continuous Integration

GitHub Actions

Runs on Python 3.9–3.13

Executes lint + type-check + test

Sends coverage to Coveralls




---

🌐 Publishing to PyPI

cp publish/.pypirc.sample ~/.pypirc  # Edit credentials
make clean
make build
make publish  # or: make publish-test


---

🎯 Goals

This template helps you:

Start with a modern and modular Python layout

Build a CLI tool with fallback to importable library usage

Apply log rotation and per-environment logging

Achieve full test coverage with minimal noise

Support real-world workflows via CI, PyPI, and .env overrides



---

📄 License

MIT License © 2025 berserkhmdvhb

