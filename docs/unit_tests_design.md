# ✅ Testing Strategy

This document explains the comprehensive testing approach used in the `myproject` CLI tool. The project emphasizes clean test separation, reproducibility, and full coverage with realistic CLI simulation.

---

## 📂 Table of Contents

* [📝 Overview](#-overview)
* [🔢 Testing Layers](#-testing-layers)
* [🔹 Unit Tests](#-unit-tests)
* [🔹 CLI Integration Tests](#-cli-integration-tests)
* [🧹 Fixtures and Utilities](#-fixtures-and-utilities)
* [💡 Debug and Log Testing](#-debug-and-log-testing)
* [🔍 Coverage and Linting](#-coverage-and-linting)
* [🔗 Related](#-related)
* [✅ Summary](#-summary)

---

## 📝 Overview

Testing is split into **unit-level** validation for individual functions/modules and **integration tests** that invoke the CLI as a real subprocess. The goal is to:

* Ensure correctness and edge-case handling
* Test realistic CLI behavior with real argument parsing and env handling
* Prevent regressions when refactoring
* Maintain 100% coverage across all files

---

## 🔢 Testing Layers

| Layer         | Scope                              | Files Affected                     |
| ------------- | ---------------------------------- | ---------------------------------- |
| Unit Tests    | Logic in isolation                 | `test_core.py`, `test_settings.py`  |
| CLI Tests     | Full CLI simulation                | `test_cli_main.py`, `test_args.py`, `test_diagnostics.py`, `test_handlers.py`, `test_parser.py`, `test_utils_color.py`, `test_utils_logger.py`|
| Logging Tests | Rotation, output routing, teardown | `test_utils_logger.py`             |
| Diagnostics   | Dotenv and debug CLI feedback      | `test_settings.py`, `test_main.py` |

---

## 🔹 Unit Tests

Each module is tested in isolation.
From CLI modules:

* `cli_main.py`:
* `args.py`: ...
* `parser.py`: ...
* `handlers.py`: ...
* `utils_color.py`: formatting ANSI escape wrappers
* `utils_logger.py`: handler setup, rotation logic, teardown behavior

From core moduels:
* `core.py`: processing behavior, uppercase logic, fallback logic
* `settings.py`: `.env` resolution, override rules, config parsing

> Mocking and monkeypatching are used to avoid real file/OS interactions.

---

## 🔹 CLI Integration Tests

* Simulate real CLI usage via subprocesses
* Use `run_cli` fixture to invoke `myproject` via its installed entry point
* Validate:

  * Output formatting
  * Exit codes
  * Environment handling (`--env`, `.env.test`, etc.)
  * Logging output
  * Debug diagnostics

Example:

```python
result = run_cli(["--query", "hello", "--debug"])
assert result.returncode == 0
assert "Processed" in result.stdout
```

These simulate full lifecycle from CLI entry point to stdout/stderr.

---

## 🧹 Fixtures and Utilities

Centralized in `conftest.py`:

| Fixture                  | Purpose                                           |
| ------------------------ | ------------------------------------------------- |
| `run_cli`                | Run CLI as subprocess, capture result             |
| `log_stream`             | Capture in-memory log output                      |
| `patched_settings`       | Override settings via monkeypatch                 |
| `patch_env`              | Temporarily set environment variables             |
| `setup_test_root`        | Isolate `logs/` and `.env` in temp folder         |
| `clean_myproject_logger` | Remove handlers between tests to avoid duplicates |

---

## 💡 Debug and Log Testing

* `test_utils_logger.py` ensures logs rotate and respect `.env` size settings
* `test_settings.py` captures `.env` debug output via `print_dotenv_debug()`
* Integration tests toggle `MYPROJECT_DEBUG_ENV_LOAD` to simulate debug output
* `--color=never` ensures ANSI codes are properly skipped

---

## 🔍 Coverage and Linting

* 100% test coverage enforced via `pytest --cov`
* `make test` runs all tests + linting
* `make lint` uses:

  * Ruff for style
  * Mypy for type checking
  * Black for formatting
* GitHub Actions CI validates all PRs

---

## 🔗 Related

* [cli\_architecture.md](cli_architecture.md)
* [debug\_diagnostics.md](debug_diagnostics.md)
* [logging\_system.md](logging_system.md)

---

## ✅ Summary

The `myproject` test suite ensures correctness, coverage, and confidence in changes. It combines fast unit testing with robust CLI integration checks and full logging/diagnostic validation. The test framework is modular, isolated, and CI-friendly.
