# 🧰 python-project-template

[![License](https://img.shields.io/github/license/berserkhmdvhb/python-project-template)](LICENSE.txt)
[![Tests](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml)
[![Coverage Status](https://img.shields.io/coveralls/github/berserkhmdvhb/python-project-template?branch=main)](https://coveralls.io/github/berserkhmdvhb/python-project-template?branch=main)

A **modern, minimal, and reusable Python project template** for building libraries, CLIs, or hybrid packages — designed with best practices, rich tooling, and robust environment-based behavior.

---

## 📚 Table of Contents

* [✨ Features](#-features)
* [📦 Project Structure](#-project-structure)

  * [📂 Structure](#-structure)
  * [🧱 Architecture](#-architecture)
* [🚀 Quickstart](#-quickstart)
* [🧑‍💼 Developer Guide](#-developer-guide)
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
│       ├── cli/                       # CLI logic (modularized)
│       ├── core.py                    # Core business logic (importable)
│       ├── constants.py               # Default values, exit codes
│       ├── settings.py                # Environment variable loading
│       └── utils_logger.py            # Logging helpers
└── tests/
    ├── cli/                           # CLI test modules
    ├── test_lib.py                    # Core logic tests
    ├── test_log.py                    # Logging tests
    ├── test_settings.py               # Environment logic tests
    ├── conftest.py                    # Fixtures and test setup
    └── manual/demo.ipynb              # Playground notebook
```

### 🧱 Architecture

#### 1. **Environment Configuration**

* `settings.py`: loads `.env` files or system envs
* Supports override path, test mode, fallback chain

#### 2. **CLI Layer**

* Modular CLI: parser, handlers, formatting, logger setup
* Runs via `myproject` or `python -m myproject`

#### 3. **Core Logic**

* `core.py`: clean, reusable pure functions

#### 4. **Testing Design**

* Full isolation: core vs CLI vs env vs logger
* Hybrid tests: subprocess + unit
* 100% coverage with detailed Make targets

---

## 🚀 Quickstart

### 📥 Installation (Editable Mode)

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
make develop
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

| Command                            | Description                                                 |
| ---------------------------------- | ----------------------------------------------------------- |
| `make install`                     | Install the package in editable mode                        |
| `make develop`                     | Install with `[dev]` extras (for development)               |
| `make fmt`                         | Format code using Ruff                                      |
| `make fmt-check`                   | Check formatting without making changes                     |
| `make lint-ruff`                   | Run Ruff linter on codebase                                 |
| `make type-check`                  | Run MyPy static type checks                                 |
| `make lint-all`                    | Run format, lint, and type check                            |
| `make lint-all-check`              | Dry run of all checks                                       |
| `make test`                        | Run all tests using Pytest                                  |
| `make test-file FILE=...`          | Run a specific test file or pattern                         |
| `make test-fast`                   | Run only last failed tests                                  |
| `make test-coverage`               | Run tests and show coverage in terminal                     |
| `make test-coverage-xml`           | Generate XML coverage report (for CI tools)                 |
| `make test-cov-html`               | Generate and open HTML coverage report                      |
| `make test-coverage-rep`           | Show full line-by-line terminal report                      |
| `make test-coverage-file FILE=...` | Show coverage for a specific file                           |
| `make clean-coverage`              | Remove all cached coverage files                            |
| `make test-watch`                  | Auto-rerun tests on file changes (requires `ptw`)           |
| `make check-all`                   | Run lint, type-check, and test coverage                     |
| `make precommit`                   | Install pre-commit Git hooks                                |
| `make precommit-check`             | Dry-run all pre-commit hooks with output                    |
| `make precommit-run`               | Run all pre-commit hooks                                    |
| `make env-check`                   | Display Python version and current environment info         |
| `make env-debug`                   | Show debug-related environment variables                    |
| `make env-clear`                   | Unset `MYPROJECT_*` and `DOTENV_PATH` variables             |
| `make env-example`                 | Show example environment variable usage                     |
| `make dotenv-debug`                | Display `.env` loading debug info using internal CLI loader |
| `make safety`                      | Run `safety` checks for dependency vulnerabilities          |
| `make check-updates`               | List outdated Python packages                               |
| `make check-toml`                  | Validate `pyproject.toml` syntax                            |
| `make build`                       | Build distribution packages (`dist/`)                       |
| `make clean`                       | Remove `dist/`, `build/`, and `.egg-info`                   |
| `make clean-pyc`                   | Remove all `__pycache__` and `.pyc` files                   |
| `make clean-all`                   | Clean everything: build, cache, pyc, logs, coverage         |
| `make publish-test`                | Upload package to [TestPyPI](https://test.pypi.org/)        |
| `make publish-dryrun`              | Dry-run and validate upload to TestPyPI                     |
| `make publish`                     | Upload to real PyPI                                         |
| `make upload-coverage`             | Upload test coverage results to Coveralls                   |

---

## 🔁 Continuous Integration

* GitHub Actions CI pipeline runs on every push and PR:

  * Python 3.9 → 3.13
  * Lint (Ruff), type-check (MyPy), test (Pytest)
  * Uploads coverage to Coveralls

---

## 🌐 Publishing to PyPI

1. Configure credentials:

```bash
cp publish/.pypirc.sample ~/.pypirc
```

2. Build and publish:

```bash
make clean
make build
make publish
```

3. TestPyPI dry-run:

```bash
make publish-dryrun
```

---

## 🎯 Goals

* Start from a **best-practice Python layout**
* Deploy a **configurable CLI + reusable core lib**
* Implement **structured logging per environment**
* Automate **test, build, and release** workflows
* Maintain **100% test coverage and lint clean**
* Simulate real **project lifecycle** scenarios

---

## 📄 License

MIT License © 2025 [berserkhmdvhb](https://github.com/berserkhmdvhb)
