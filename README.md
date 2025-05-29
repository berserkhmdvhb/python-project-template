# 🧰 python-project-template

[![License](https://img.shields.io/github/license/berserkhmdvhb/python-project-template)](LICENSE.txt)
[![Tests](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/berserkhmdvhb/python-project-template/badge.svg?branch=main)](https://coveralls.io/github/berserkhmdvhb/python-project-template?branch=main)

A **modern, minimal, and reusable Python project template** for building libraries, CLIs, or hybrid packages — designed with best practices in mind.

---

## 📚 Table of Contents

- [✨ Features](#-features)  
- [📦 Project Structure](#-project-structure)  
  - [📂 Structure](#-structure)  
  - [🧱 Architecture](#-architecture)  
- [🚀 Quickstart](#-quickstart)  
- [🧑‍💼 Developer Guide](#-developer-guide)  
- [🔁 Continuous Integration](#-continuous-integration)  
- [📦 Publishing to PyPI](#-publishing-to-pypi)  
- [🎯 Goals](#-goals)  
- [📄 License](#-license)  

---

## ✨ Features

* 📜 Clean, PEP 621–compliant `pyproject.toml`  
* 🧱 Hybrid support for both CLI (`myproject`, `python -m myproject`) and importable library  
* 🔧 Environment-dependent configuration via `.env` and `settings.py` (DEV/UAT/PROD)  
* 📁 `src/` layout with clean separation of CLI logic, core library, and utilities  
* 🔍 Static analysis: `ruff` (lint/format), `mypy` (type checking)  
* 🧪 Testing: `pytest`, `coverage`, full CLI test suite, and 100% coverage on core modules  
* 📝 Log management:  
  - Per-environment log directories (`logs/DEV`, `logs/UAT`, `logs/PROD`)  
  - Rotating logs by size with configurable `LOG_MAX_BYTES` and `LOG_BACKUP_COUNT`  
* 👋 Pre-commit hooks for code quality  
* 🔁 GitHub Actions for CI (lint, typecheck, tests, coverage)  
* 🛠 Makefile for automation (dev, test, lint, release, publish)  

---

## 📦 Project Structure

### 📂 Structure

```
python-project-template/
├── .github/workflows/tests.yml       ← GitHub CI pipeline
├── .pre-commit-config.yaml           ← Pre-commit hooks
├── .pypirc.template                  ← PyPI/TestPyPI credentials template
├── LICENSE.txt                       ← MIT License
├── Makefile                          ← Dev/test/release commands
├── MANIFEST.in                       ← Packaging manifest
├── pyproject.toml                    ← Build and dependencies
├── README.md                         ← This file
├── src/
│   └── myproject/
│       ├── __init__.py               ← Defines `__version__`
│       ├── __main__.py               ← `python -m myproject`
│       ├── cli.py                    ← CLI entrypoint & args
│       ├── cli_color_utils.py        ← Color formatting utilities
│       ├── cli_logger_utils.py       ← Logging setup & teardown helpers
│       ├── constants.py              ← Exit codes, defaults, log config
│       ├── core.py                   ← Business logic / library code
│       └── settings.py               ← Env-based configuration
└── tests/
    ├── conftest.py                   ← Shared fixtures & logger cleanup
    ├── test_cli.py                   ← CLI integration tests
    ├── test_lib.py                   ← Core library tests
    ├── test_log.py                   ← Logging behavior & rotation tests
    └── manual/
        └── demo.ipynb                ← Notebook for interactive testing
```

### 🧱 Architecture

The project is organized for **modularity, reusability, and clarity**:

* `src/myproject/__main__.py` allows direct module execution (`python -m myproject`)  
* `cli.py` contains CLI logic separated from business logic  
* `cli_color_utils.py` centralizes color formatting and ANSI handling  
* `cli_logger_utils.py` handles environment-aware, rotating file logging  
* `core.py` hosts library functions with full test coverage  
* `constants.py` and `settings.py` drive configuration and defaults  

This architecture ensures:

* **Separation of concerns** between CLI and core logic  
* **Extensibility** for growing features  
* **Testability** with isolated units for CLI, core, and logging  

---

## 🚀 Quickstart

### 📥 Installation (Editable Mode)

```bash
python -m venv .venv
source .venv/bin/activate          # or .venv\Scripts\activate on Windows
make develop                       # or: pip install -e .[dev]
```

### 🗅 CLI Usage

```bash
myproject --version
myproject --query "hello"
python -m myproject --help
```

---

## 🧑‍💼 Developer Guide

### 🛠 Makefile Commands

| Command                | Description                              |
| ---------------------- | ---------------------------------------- |
| `make help`            | Show available commands                  |
| `make install`         | Install package (editable mode)          |
| `make develop`         | Install with dev dependencies (`.[dev]`) |
| `make format`          | Auto-format with Ruff                    |
| `make lint`            | Run Ruff + MyPy for lint/typecheck       |
| `make test`            | Run all tests (`pytest -v`)              |
| `make test-fast`       | Re-run only last failed tests            |
| `make coverage`        | Show coverage in terminal                |
| `make coverage-xml`    | Generate XML for CI/Coveralls            |
| `make upload-coverage` | Upload to Coveralls (`python -m coveralls`) |
| `make precommit`       | Install pre-commit hooks                 |
| `make precommit-run`   | Run pre-commit on all files              |
| `make build`           | Build distributions (`python -m build`)  |
| `make clean`           | Remove build artifacts (`dist/`, etc.)   |
| `make publish-test`    | Upload to TestPyPI                       |
| `make publish`         | Upload to PyPI                           |

### 📋 Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

---

## 🔁 Continuous Integration

- **GitHub Actions** (`.github/workflows/tests.yml`):
- Python 3.9–3.13 matrix  
- `make lint`, `make test`, `make coverage-xml`  
- Optional Coveralls upload  

---

## 📦 Publishing to PyPI

1. Copy `.pypirc.template` to `~/.pypirc` and insert your tokens.  
2. Build and publish:

   ```bash
   make build
   twine upload dist/*
   ```

3. For TestPyPI:

   ```bash
   make publish-test
   ```

---

## 🎯 Goals

Use this template to:

* Start with a **modern Python project layout**  
* Support **environment-aware configuration**  
* Ship **both CLI and library** in one package  
* Maintain **code quality** with linting, typing, testing, and logs  
* Automate workflows via **Make, pre-commit, CI, and tests**  

---

## 📄 License

MIT © berserkhmdvhb 2025
