# 🧰 python-project-template

[![License](https://img.shields.io/github/license/berserkhmdvhb/python-project-template)](LICENSE.txt)
[![Tests](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/berserkhmdvhb/python-project-template/badge.svg?branch=main&t=force-refresh)](https://coveralls.io/github/berserkhmdvhb/python-project-template?branch=main)

A **modern, minimal, and reusable Python project template** for building libraries, CLIs, or hybrid packages — designed with best practices, rich tooling, and robust environment-based behavior.

---

## 📚 Table of Contents

* [✨ Features](#-features)
* [📦 Project Structure](#-project-structure)
  * [📂 Structure](#-structure)
  * [🧱 Architecture](#-architecture)
* [🚀 Quickstart](#-quickstart)
* [🧑‍💼 Developer Guide](-developer-guide)
* [🔁 Continuous Integration](#-continuous-integration)
* [🌐 Publishing to PyPI](#-publishing-to-pypi)
* [🎯 Goals](#-goals)
* [📄 License](#-license)

---

## ✨ Features

* 📜 Modern `pyproject.toml` (PEP 621) for build and metadata
* 🧱 Clean hybrid architecture: CLI and importable core library
* 🔧 Environment-dependent behavior (DEV, UAT, PROD, TEST)
* 📁 Structured logging with:

  * Named log folders per environment (`logs/ENV/`)
  * Log rotation using `RotatingFileHandler`
  * Configurable limits via `.env` or system vars
* 📄 Robust environment management:

  * Automatic `.env` file detection
  * Manual `.env` override with `--dotenv-path`
  * Test-aware loading via `PYTEST_CURRENT_TEST`
* 🔍 Quality tools:

  * `ruff` (format/lint), `mypy` (type-check), `pytest`, `coverage`
  * Pre-commit hooks for consistent code hygiene
* ⚖️ Fully tested CLI (`myproject`) and library (`myproject.core`) with 100% coverage
* 🚧 Developer tooling:

  * `Makefile` commands
  * `conftest.py` with modular fixtures
  * GitHub Actions CI
* 🌐 PyPI-ready: Includes sample `.pypirc`, build, and publish steps

---

## 📦 Project Structure

### 📂 Structure

```
python-project-template/
├── .github/workflows/tests.yml        # GitHub CI pipeline
├── .pre-commit-config.yaml            # Pre-commit hooks
├── publish/
│   └── .pypirc.sample                 # Sample config for PyPI/TestPyPI
├── .env.sample                        # Environment variable sample
├── LICENSE.txt
├── Makefile                           # Automation for dev/test/publish
├── MANIFEST.in                        # Include files in sdist
├── pyproject.toml                     # PEP 621 build + deps
├── README.md
├── src/
│   └── myproject/
│       ├── __init__.py                # Version metadata
│       ├── __main__.py                # Entry: python -m myproject
│       ├── cli.py                     # CLI parser and command handler
│       ├── cli_color_utils.py         # Colorized terminal output
│       ├── cli_logger_utils.py        # Logging setup, rotation, teardown
│       ├── constants.py               # Default values, exit codes
│       ├── core.py                    # Core business logic (importable)
│       └── settings.py                # Environment variable loading
└── tests/
    ├── conftest.py                    # Fixtures and logger setup
    ├── test_cli.py                    # CLI integration tests
    ├── test_cli_env.py                # Env behavior for CLI
    ├── test_cli_logger_utils.py       # Logger rotation and setup
    ├── test_lib.py                    # Core logic tests
    ├── test_log.py                    # Logging config/rotation
    ├── test_settings.py               # Env detection logic
    └── manual/demo.ipynb              # Playground notebook
```

### 🧱 Architecture

This template is structured around **clarity**, **testability**, and **flexible deployment**. It separates:

#### 1. **Environment Configuration**

* `settings.py`: Loads env vars using `dotenv`, `os.environ`, and supports:

  * Automatic `.env` detection
  * Manual path override (via `--dotenv-path` or `DOTENV_PATH`)
  * Prioritized order: `PYTEST_CURRENT_TEST` → CLI arg → `DOTENV_PATH` → `.env*` fallback

#### 2. **CLI Layer**

* `cli.py`: Main argument parsing (`argparse`) and command routing
* `cli_color_utils.py`: Shared output formatting utilities
* `cli_logger_utils.py`: Log rotation, colored logs, auto folder setup per env
* Supports command-line usage (`myproject`) and module usage (`python -m myproject`)

#### 3. **Core Logic**

* `core.py`: Pure functions and logic reusable from both CLI and other tools
* Fully typed and tested independently

#### 4. **Testing Design**

* Isolated test modules for CLI, logger, envs, and core
* Environment simulation with PowerShell/Linux support
* Test CLI using subprocess + direct calls
* Log rotation and log-level tests using dynamic values from `.env`

---

## 🚀 Quickstart

### 📥 Installation (Editable Mode)

```bash
python -m venv .venv
source .venv/bin/activate          # or .venv\Scripts\activate on Windows
make develop                       # or: pip install -e .[dev]
```

### 💻 CLI Usage

```bash
myproject --version
myproject --query "hello"
python -m myproject --help
```

---

## 🧑‍💼 Developer Guide

### 🔧 Makefile Commands

| Command                | Description                       |
| ---------------------- | --------------------------------- |
| `make help`            | List available commands           |
| `make install`         | Install project in editable mode  |
| `make develop`         | Install with `[dev]` dependencies |
| `make format`          | Format code using Ruff            |
| `make lint`            | Lint + type check                 |
| `make test`            | Run all unit + integration tests  |
| `make test-fast`       | Re-run failed tests only          |
| `make coverage`        | View test coverage in terminal    |
| `make coverage-xml`    | Export XML coverage for CI        |
| `make upload-coverage` | Upload results to Coveralls       |
| `make precommit`       | Set up pre-commit hooks           |
| `make precommit-run`   | Run hooks against all files       |
| `make build`           | Create package distributions      |
| `make clean`           | Remove build artifacts            |
| `make publish-test`    | Push to TestPyPI                  |
| `make publish`         | Push to PyPI                      |

### 📋 Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

---

## 🔁 Continuous Integration

* GitHub Actions CI runs:

  * Python 3.9 to 3.13 matrix
  * Lint, type-check, and test
  * Coverage uploaded to Coveralls

---

## 🌐 Publishing to PyPI

1. Copy `.pypirc.sample` to `~/.pypirc` and configure credentials.

2. Build and publish:

```bash
make clean
make build
make publish
```

3. Or for TestPyPI:

```bash
make publish-test
```

---

## 🎯 Goals

This project template aims to help you:

* Start from a **best-practice Python layout**
* Deploy **configurable CLI + importable library**
* Implement **log rotation** + structured logs per environment
* Enforce **code quality** with lint, type checks, and full testing
* Document **behavioral scenarios** (see [`docs/env-logging-scenarios.md`](docs/env-logging-scenarios.md))
* Automate testing and packaging workflows

---

## 📄 License

MIT License © 2025 [berserkhmdvhb](https://github.com/berserkhmdvhb)
