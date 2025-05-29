# 🧰 python-project-template
[![License](https://img.shields.io/github/license/berserkhmdvhb/python-project-template)](LICENSE.txt)
[![Tests](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml/badge.svg)](https://github.com/berserkhmdvhb/python-project-template/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/berserkhmdvhb/python-project-template/badge.svg?branch=main)](https://coveralls.io/github/berserkhmdvhb/python-project-template?branch=main)

A **modern, minimal, and reusable Python project template** for building libraries, CLIs, or hybrid packages — designed with best practices in mind.

---

## 📦 Features

* 📜 Clean, PEP 621-compliant `pyproject.toml`
* 🧱 Hybrid support for both CLI (`myproject`, `python -m myproject`) and importable library
* 📁 Source layout with `src/myproject/` package
* ✅ Static analysis: `ruff` (linting, formatting), `mypy` (type checking)
* 🧪 Testing: `pytest`, `coverage`, full CLI test suite
* 📋 Pre-commit hook support
* 🔁 GitHub Actions for CI: test, lint, typecheck, coverage
* 🛠 Makefile for automation (dev/test/release)

---

## 📂 Project Structure

```
python-project-template/
├── .github/workflows/tests.yml       ← GitHub CI
├── .pre-commit-config.yaml           ← Format/lint/typecheck hooks
├── LICENSE.txt                       ← MIT License
├── Makefile                          ← Common development commands
├── MANIFEST.in                       ← Packaging manifest
├── pyproject.toml                    ← Config + dependencies
├── README.md                         ← You're reading it
├── src/
│   └── myproject/
│       ├── __init__.py               ← Defines __version__
│       ├── __main__.py               ← Enables `python -m myproject`
│       ├── cli.py                    ← CLI logic
│       ├── cli_color_utils.py        ← Color utils and formatting
│       └── constants.py              ← Exit codes, defaults, enum types
└── tests/
    ├── test_cli.py                   ← Full CLI test suite
    ├── test_lib.py                   ← Placeholder for library tests
    └── manual/
        └── demo.ipynb                ← Manual CLI dev/test notebook
```

---

## 🚀 Quickstart

### 📥 Installation (Editable Mode)

```bash
python -m venv .venv
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows
make develop               # or: pip install -e .[dev]
```

### 🖥 CLI Usage

```bash
myproject --version
python -m myproject --version
```

> ⚠️ `myproject` is a placeholder name — replace it with your actual package and logic.

---

## 🧑‍💻 Developer Guide

### 🛠 Makefile Commands

| Command              | Description                                 |
|----------------------|---------------------------------------------|
| `make help`          | Show available commands                     |
| `make install`       | Install package (editable mode)             |
| `make develop`       | Install with dev dependencies               |
| `make lint`          | Run Ruff and MyPy                           |
| `make format`        | Auto-format with Ruff                       |
| `make test`          | Run all tests                               |
| `make test-fast`     | Re-run only last failed tests               |
| `make coverage`      | Show test coverage in terminal              |
| `make coverage-xml`  | Generate XML for CI or Coveralls            |
| `make check-all`     | Run format, lint, and test coverage         |
| `make precommit`     | Install pre-commit hooks                    |
| `make precommit-run` | Run all pre-commit hooks                    |
| `make build`         | Build package for distribution              |
| `make clean`         | Remove dist/build artifacts                 |


You can also run tools directly:

```bash
ruff check src/ tests/
mypy src/ tests/
pytest -v
```

### 📋 Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

---

## 🔁 Continuous Integration

GitHub Actions workflow: `.github/workflows/tests.yml`

* Python 3.9 through 3.13
* Linting (`ruff`), type-checking (`mypy`)
* Full test suite (`pytest`) with coverage
* Optional Coveralls integration

---

## 🎯 Goals

Use this template if you want to:

* Start with a **modern Python project layout**
* Support **both CLI and library usage**
* Automate development with **Make, CI, pre-commit**
* Follow **clean code and testing best practices**

---

## 📄 License

MIT © berserkhmdvhb 2025
