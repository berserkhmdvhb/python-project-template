# 📦 CLI Architecture

This document describes the internal architecture of the `myproject` CLI, designed to be modular, testable, and robust. It also highlights key components and how they interact.

---

## 🧭 Overview

The CLI is structured around a layered model, separating parsing, logic, and output. Its entry point is the `myproject` command or `python -m myproject`, which triggers a well-organized flow of:

1. Environment loading
2. Argument parsing
3. Logging setup
4. Query processing
5. Output handling

---

## 🗂️ File Structure

```
src/myproject/
├── __main__.py            # Python entry point (calls main())
├── cli/
│   ├── __init__.py
│   ├── main.py            # CLI entry dispatcher
│   ├── cli_main.py        # Core CLI logic
│   ├── parser.py          # Argparse CLI parser
│   ├── handlers.py        # Routes to business logic
│   ├── color_utils.py     # Styled output (info, error, hint)
│   └── logger_utils.py    # Logging setup and teardown
```

---

## 🚀 CLI Entry Flow

### 1. **`__main__.py`**

The CLI is executable via `python -m myproject`, which delegates to `cli.main()`.

```python
from myproject.cli import main
main()
```

### 2. **`cli/main.py`**

This module initializes the CLI by calling `cli_main.main(argv)` and ensures the environment is loaded early.

```python
def main(argv: list[str] | None = None) -> None:
    cli_main.main(argv)
```

### 3. **`cli/cli_main.py`**

This is the command router and coordinator:

* Loads environment (`load_settings()`)
* Parses arguments using `parser.py`
* Conditionally activates `argcomplete`
* Applies logging settings
* Calls handlers to process the query
* Prints or logs result depending on `--verbose`/`--format`

```python
if ARGCOMPLETE_AVAILABLE:
    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except Exception as exc:
        logger.debug("argcomplete setup failed: %s", exc)
```

Handles exit codes and error routing as defined in `constants.py`.

---

## 🧰 Parser Design (`parser.py`)

* Implements `argparse.ArgumentParser`
* Defines top-level CLI options (`--query`, `--format`, `--env`, `--dotenv-path`, `--verbose`, `--debug`)
* Early parses `--env` and `--dotenv-path` before main settings load
* Exposes the parser for `argcomplete`

---

## 🛣️ Handler Routing (`handlers.py`)

Routes parsed `args` to business logic:

* Uses `args.query` as input
* Invokes `process_query_or_simulate()` from the core logic
* Chooses `handle_result()` method based on `--format` (text or JSON)

---

## 🎨 Output Styling (`color_utils.py`)

* Provides `format_info`, `format_error`, and `format_hint`
* Applies ANSI color codes only if `--color` is not `never`
* Auto-detects terminal support

---

## 📝 Logging Setup (`logger_utils.py`)

* Configures per-env log directory: `logs/ENV/`
* Uses `RotatingFileHandler` with size and count control
* Sets global log level based on `--verbose`
* Fully testable via mock handlers and temp dirs

---

## 🧪 Testing the CLI

* CLI tested with `subprocess` and `argparse.Namespace`
* Full integration coverage
* Log and environment patching via `conftest.py`
* `argcomplete` failure is tested by injecting a stub module

---

## ✅ Summary

The CLI architecture is modular, predictable, and environment-aware. It separates parsing, logic, and output cleanly, and is designed for testability from the ground up.
