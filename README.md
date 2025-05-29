# 🧰 python-project-template


[![License](https://img.shields.io/github/license/berserkhmdvhb/python-project-template)](LICENSE.txt)

[![Tests](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml)

[![Coverage Status](https://coveralls.io/repos/github/berserkhmdvhb/python-project-template/badge.svg?branch=main)](https://coveralls.io/github/berserkhmdvhb/python-project-template?branch=main)

A **modern, minimal, and reusable Python project template** for building libraries, CLIs, or hybrid packages — designed with best practices in mind.

---

## 📚 Table of Contents

- [✨ Features](#-features)  
- [📦 Project Structure](#-project-structure)  
- [🚀 Quickstart](#-quickstart)  
- [🧑‍💼 Developer Guide](#-developer-guide)  
- [🔁 Continuous Integration](#-continuous-integration)  
- [📦 Publishing to PyPI](#-publishing-to-pypi)  
- [🎯 Goals](#-goals)  
- [📄 License](#-license)  

---

## ✨ Features

- 📜 PEP 621–compliant `pyproject.toml`  
- 🧱 Hybrid support for both CLI (`myproject`, `python -m myproject`) and importable library  
- 🔧 Environment-dependent configuration via `.env` and `settings.py` (DEV/UAT/PROD)  
- 📁 `src/` layout with clean separation of CLI logic, core library, and utilities  
- 🔍 Static analysis: `ruff` (lint/format), `mypy` (type checking)  
- 🧪 Testing: `pytest`, `coverage`, 100% coverage on core modules, CLI, and logging  
- 📝 Log management:  
  - Per-environment log directories (`logs/DEV`, `logs/UAT`, `logs/PROD`)  
  - Rotating logs by size with configurable `LOG_MAX_BYTES` and `LOG_BACKUP_COUNT`  
- 👋 Pre-commit hooks for code quality  
- 🔁 GitHub Actions for CI (lint, typecheck, tests, coverage)  
- 🛠 Makefile with common workflows: dev, test, lint, release  

---

## 📦 Project Structure

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
│       ├── __init__.py               ← Package version
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

---

## 🚀 Quickstart

### 1. Create virtual environment & install

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
make develop                # installs editable package + dev dependencies
```

### 2. Configure environment

Copy the template for PyPI publishing (optional):

```bash
cp .pypirc.template ~/.pypirc
# edit ~/.pypirc, replacing <your-token> placeholders
```

Set your runtime environment in `.env`:

```ini
MYPROJECT_ENV=DEV
LOG_MAX_BYTES=1000000
LOG_BACKUP_COUNT=5
```

### 3. Run CLI

```bash
myproject --help
myproject --query "hello"
python -m myproject --version
```

---

## 🧑‍💼 Developer Guide

### Makefile commands

| Command                | Description                              |
| ---------------------- | ---------------------------------------- |
| `make help`            | List all commands                       |
| `make install`         | `pip install -e .`                      |
| `make develop`         | `pip install -e .[dev]`                 |
| `make format`          | `ruff format src/ tests/`               |
| `make lint`            | `ruff check` + `mypy src/ tests/`       |
| `make test`            | `pytest -v`                             |
| `make test-fast`       | `pytest --lf -x -v`                     |
| `make coverage`        | `pytest --cov=myproject --cov-report=term` |
| `make coverage-xml`    | `pytest --cov=myproject --cov-report=xml` |
| `make upload-coverage` | `python -m coveralls`                   |
| `make precommit`       | `pre-commit install`                    |
| `make precommit-run`   | `pre-commit run --all-files`            |
| `make build`           | `python -m build`                       |
| `make clean`           | remove `dist/`, `build/`, `*.egg-info`  |
| `make publish-test`    | Upload to TestPyPI                      |
| `make publish`         | Upload to PyPI                          |

---

## 🔁 Continuous Integration

- **GitHub Actions** (`.github/workflows/tests.yml`):
  - Python 3.9–3.13 matrix
  - `make lint`, `make test`, `make coverage-xml`
  - Optional Coveralls upload

---

## 📦 Publishing to PyPI

1. Add your credentials to `~/.pypirc` from the [template](.pypirc.template).  
2. Build & publish:

   ```bash
   make build
   twine upload dist/*
   ```

3. To TestPyPI:

   ```bash
   make publish-test
   ```

---

## 🎯 Goals

Use this template to:

- Kickstart a **modern Python project**  
- Support **environment-aware configuration**  
- Ship **both CLI and library** in one package  
- Ensure **quality** with linting, typing, testing, and logs  
- Automate workflows via **Make, pre-commit, CI, and tests**  

---

## 📄 License

MIT © berserkhmdvhb 2025
