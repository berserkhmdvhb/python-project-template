# 🧰 python-project-template

[![License](https://img.shields.io/github/license/berserkhmdvhb/python-project-template)](LICENSE)
[![Tests](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/berserkhmdvhb/python-project-template/badge.svg?branch=main&nocache=1)](https://coveralls.io/github/berserkhmdvhb/python-project-template?branch=main)


A **modern and reusable Python project template** for building libraries, CLIs, or hybrid packages — designed with best practices, rich tooling, and robust environment-based behavior.

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
* [📖 Documentation](#-documentation)
* [🎯 Goals](#-goals)
* [📄 License](#-license)

---

## ✨ Features

* 📜 Modern `pyproject.toml` (PEP 621) for build and metadata
* 🧱 Hybrid architecture: CLI and importable core library
* 🔧 Environment-dependent behavior (DEV, UAT, PROD, TEST)
* 📁 Structured logging with:

  * Rotating logs under `logs/{ENV}/`
  * Configurable limits via `.env` or system vars
* 📄 Robust environment management:
  * Automatic `.env` detection and loading
  * Manual override via `--dotenv-path`
  * Test-aware fallback via `PYTEST_CURRENT_TEST`
* 🔍 Code quality and enforcement:
  * `ruff` (format/lint), `mypy` (type-check)
* ⚙️ Fully tested CLI (`myproject.cli`) and library (`myproject.core`) with 100% coverage.
* 🛠️ Developer-friendly tooling:

  * `Makefile` commands
  * `conftest.py` with modular fixtures
  * GitHub Actions CI
* 🌐 PyPI-ready: Includes `pypirc`, publish automation, metadata

---

## 📦 Project Structure

### 📂 Structure

```
python-project-template/
├── .github/workflows/tests.yml        # GitHub CI pipeline
├── .pre-commit-config.yaml            # Pre-commit hooks
├── publish/
│   └── .pypirc.sample                 # Sample config for PyPI/TestPyPI
├── .env.sample                        # Sample environment variables
├── LICENSE.txt
├── Makefile                           # Automation tasks
├── MANIFEST.in                        # Files to include in sdist
├── pyproject.toml                     # PEP 621 build + deps
├── README.md
├── src/
│   └── myproject/
│       ├── __init__.py                # Version metadata
│       ├── __main__.py                # Entry: python -m myproject
│       ├── cli/                       # CLI logic (modularized)
│       ├── core.py                    # Core business logic (importable)
│       ├── constants.py               # Default values, exit codes
│       ├── settings.py                # Environment and config handling
│       └── utils_logger.py            # Logging setup
└── tests/
    ├── cli/                           # CLI test modules
    ├── test_lib.py                    # Core logic tests
    ├── test_log.py                    # Logging tests
    ├── test_settings.py               # Env and config tests
    ├── conftest.py                    # Shared fixtures and test setup
    └── manual/demo.ipynb              # Sandbox notebook
```

### 🧱 Architecture


This project follows a layered architecture emphasizing modularity, testability, automation, and separation of concerns.

#### 1. **Configuration Layer (`settings.py`)**

Handles environment setup and `.env` management:


* Loads variables from system or `.env*` files (fallback chain)
* Respects CLI overrides (`--env`, `--dotenv-path`)
* Supports debug output via `MYPROJECT_DEBUG_ENV_LOAD`
* Smart behavior in test mode (`PYTEST_CURRENT_TEST`)

A summary of environments and env. files peresent, and the mechanism to manage and prioritize them are provided in table below. For a thorugh and detailed explanation and demo, pelase visit [docs/env-logging-scenarios.md](https://github.com/berserkhmdvhb/python-project-template/blob/main/docs/env-logging-scenarios.md). 

| Priority | File            | Loaded When                   | Purpose / Use Case                                               | Committed to Git? | Override Others?   |
| -------- | --------------- | ----------------------------- | ---------------------------------------------------------------- | ----------------- | ------------------ |
| 1️⃣      | `DOTENV_PATH`   | Set via environment variable  | Force a custom env file at runtime (e.g. for advanced CLI usage) | ❌ (user-defined)  | ✅                  |
| 2️⃣      | `.env.override` | Exists in project root        | Enforced values (CI/CD, production)                              | ✅                 | ✅                  |
| 3️⃣      | `.env`          | Exists in project root        | Main team-shared configuration                                   | ✅                 | ✅ (if no override) |
| 4️⃣      | `.env.local`    | Exists in project root        | Developer-specific overrides (not shared)                        | ❌ (`.gitignore`)  | ✅ (over `.env`)    |
| 5️⃣      | `.env.test`     | Running under `pytest`        | Clean isolation for tests                                        | ✅ (optional)      | ✅ (in test mode)   |
| 6️⃣      | `.env.sample`   | None of the above are present | Documentation or last-resort fallback                            | ✅                 | 🚫                 |

> Note: This management or environments and prioritizing them is implemented in `src/myproject/settings.py`
#### 2. **CLI Layer (`cli/`)**

Handles user interaction and command routing:

* `main.py`: Entrypoint CLI dispatcher (run via `myproject` or `python -m`)
* `parser.py`: Parses arguments with early env loading
* `cli_main.py`: Coordinates CLI logic and handles output formatting
* `handlers.py`: Routes commands to logic
* `color_utils.py`: Handles styled terminal output (info, error, hint)
* `logger_utils.py`: Sets up logging with rotation and per-env folders

#### 3. **Core Layer (`core.py`)**

Holds the core logic / business rules:

* Pure, reusable functions
* Independent of CLI or environment setup
* Fully typed and testable in isolation

#### 4. **Utility Layer**

* `constants.py`: Centralized default values and exit codes
* `utils_logger.py`: Shared logging utilities and handlers

#### 5. **Test Suite (`tests/`)**

* Fully modular: core, CLI, settings, logging each tested in isolation
* Uses `pytest`, `pytest-cov`, and `subprocess` for CLI integration tests
* Custom fixtures in `conftest.py` simulate logging, temp envs, etc.
* Achieves and enforces **95% test coverage**

---

## 🚀 Quickstart

### 📥 Installation (Editable Mode)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
make develop
```

### 💻 CLI Usage

```bash
myproject --version
myproject --query "hello world"
python -m myproject --help
```

---

## 🧑‍💼 Developer Guide

### 🔧 Makefile Commands

| Command                             | Description                                                 |
| ----------------------------------- | ----------------------------------------------------------- |
| `make install`                      | Install the package in editable mode                        |
| `make develop`                      | Install with `[dev]` extras (for development)               |
| `make fmt`                          | Format code using Ruff                                      |
| `make fmt-check`                   | Check formatting without making changes                     |
| `make lint-ruff`                   | Run Ruff linter on codebase                                 |
| `make type-check`                  | Run MyPy static type checks                                 |
| `make lint-all`                    | Run format, lint, and type check                            |
| `make lint-all-check`             | Dry run of all checks                                       |
| `make test`                         | Run all tests using Pytest                                  |
| `make test-file FILE=...`          | Run a specific test file or pattern                         |
| `make test-file-function FILE=... FUNC=...` | Run a specific test function in a file           |
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
| `make env-show`                    | Show currently set `MYPROJECT_*` and `DOTENV_PATH` vars     |
| `make env-example`                 | Show example environment variable usage                     |
| `make dotenv-debug`                | Display `.env` loading debug info using internal CLI loader |
| `make safety`                      | Run `safety` checks for dependency vulnerabilities          |
| `make check-updates`              | List outdated Python packages                               |
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

* GitHub Actions CI pipeline runs on push and PR:

  * Python 3.10 → 3.13
  * Lint/Format (Ruff), type-check (MyPy), test (Pytest)
  * Uploads coverage to Coveralls

---

## 🌐 Publishing to PyPI

1. Configure credentials:

```bash
cp publish/.pypirc.sample ~/.pypirc
```

2. Build and release:

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

## 📖 Documentation

The `docs/` directory contains detailed internal documentation covering design decisions, implementation patterns, CLI architecture, debug output, logging strategy, and more.

| Document                                                    | Description                                                                  |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------- |
| [`cli_architecture.md`](docs/cli_architecture.md)           | Overview of CLI modules, their flow, entry points, and command routing logic |
| [`core_logic.md`](docs/core_logic.md)                       | Core logic in `core.py`: processing rules, transformations, structure        |
| [`environment_config.md`](docs/environment_config.md)       | How `.env` files are resolved and prioritized across environments            |
| [`logging_system.md`](docs/logging_system.md)               | Setup and teardown of structured logging per environment, with rotation      |
| [`debug_diagnostics.md`](docs/debug_diagnostics.md)         | Debug and diagnostic output systems, `--debug`, `MYPROJECT_DEBUG_ENV_LOAD`   |
| [`test_strategy.md`](docs/test_strategy.md)                 | Testing layers, fixtures, CLI integration vs. unit testing, coverage tactics |
| [`env-logging-scenarios.md`](docs/env-logging-scenarios.md) | End-to-end `.env` and logging scenarios, edge cases and fallback resolution  |


> These documents are designed to be both developer-facing and audit-ready — helpful for onboarding, troubleshooting, and future refactoring.


---

## 🎯 Goals

* Start from a best-practice Python layout.
* Deploy a configurable CLI + reusable core lib.
* Implement structured logging per environment.
* Automate test, build, coverage, packagin, and release workflows
* Maintain 100% test coverage and strict lint.
* Simulate realistic development lifecycle

---

## 📄 License

MIT License © 2025 [berserkhmdvhb](https://github.com/berserkhmdvhb)
