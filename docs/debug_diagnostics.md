# 🛠️ Diagnostics & Debug Output

This document explains the internal diagnostics and debug features implemented in the `myproject` CLI. These tools aid development, troubleshooting, and configuration transparency.

---

## 📚 Table of Contents

* [🧽 Overview](#-overview)
* [🗂️ Files Involved](#-files-involved)
* [⚙️ Diagnostic Behavior](#-diagnostic-behavior)
* [⚙️ Dotenv Debug Output](#-dotenv-debug-output)
* [🧪 Debug Output in Tests](#-debug-output-in-tests)
* [📦 Implementation Details](#-implementation-details)
* [🔗 Related](#-related)
* [✅ Summary](#-summary)

* 

---

## 🧭 Overview

The CLI includes built-in diagnostic output to:

* Reveal how environment variables are resolved
* Print active settings after parsing and loading
* Aid debugging during development or CI/CD
* Ensure that `.env` resolution and logging setup are traceable


These are vital for diagnosing misconfigurations and debugging behavior without diving into the code.
The outputs are tightly integrated with `--debug`, `--verbose`, and the `MYPROJECT_DEBUG_ENV_LOAD` environment variable.

---


## 🗂️ Files Involved

| File               | Responsibility                                                |
| ------------------ | ------------------------------------------------------------- |
| `diagnostics.py`   | Defines debug output functions                                |
| `cli_main.py`      | Calls debug functions when `--debug` is enabled               |
| `settings.py`      | Supplies loaded configuration for diagnostic display          |
| `conftest.py`      | Enables test-mode env flags for debug simulation              |
| `test_settings.py` | Validates `print_dotenv_debug()` and CLI debug behavior       |
| `test_main.py`     | Captures and asserts on debug output from CLI subprocess runs |

---
## ⚙️ Diagnostic Behavior

Diagnostic output is controlled by:

1. The CLI argument: `--debug`
2. The environment variable: `MYPROJECT_DEBUG_ENV_LOAD=1`

> Both can work independently or together, and they are parsed early via `apply_early_env()` in `parser.py`.

| Trigger                      | Output Scope                                 | When to Use                               |
| ---------------------------- | -------------------------------------------- | ----------------------------------------- |
| `--debug`                    | Full diagnostics + DEBUG logging             | CLI development, troubleshooting          |
| `--verbose`                  | INFO-level output to stdout                  | Basic inspection of CLI processing        |
| `MYPROJECT_DEBUG_ENV_LOAD=1` | Prints resolved `.env` sources and locations | Investigate which dotenv files are loaded |

All debug output is written to stdout (not stderr) and respects the `--color` flag.

---

### Debug Functions: 

#### `print_debug_diagnostics(args, settings, use_color)`

```python
def print_debug_diagnostics(
    args: Namespace,
    settings: Settings,
    use_color: bool,
) -> None:
```

🔹 **Purpose**:
Prints internal CLI and settings state in a structured format.

🔹 **Output Includes**:

* Raw parsed arguments (`args`)
* Loaded `settings` values
* Flags like `debug`, `verbose`, `env`, etc.

🔹 **Behavior**:

* Formats using `format_hint()` or plain `str()`
* Handles `Namespace` and `BaseSettings` introspection
* Uses `pformat()` for human-readable output
* Writes directly to `stdout` (not logger)

🔹 **Example Output**:

```
[debug] CLI args:
Namespace(query='foo', debug=True, ...)

[debug] Settings:
Settings(env='DEV', log_level='DEBUG', ...)
```


---

#### `print_dotenv_debug(settings, debug, use_color)`

```python
def print_dotenv_debug(
    settings: Settings,
    debug: bool,
    use_color: bool,
) -> None:
```

🔹 **Purpose**:
Show which `.env` files were loaded, and their source priority.

🔹 **Conditions**:

* Runs **only** if the env var `MYPROJECT_DEBUG_ENV_LOAD=1`
* Executed during `cli_main.main()`, **before** any CLI logic runs

🔹 **Output**:

* `DOTENV_PATH` usage
* File loading fallbacks: `.env.override`, `.env`, `.env.local`, etc.
* Current values of key `MYPROJECT_` variables

🔹 **Internals**:

* Uses `settings.dotenv_path_source` to track origin
* Tries to give the user **transparency over env logic**

---

## ⚙️ Dotenv Debug Output

If `MYPROJECT_DEBUG_ENV_LOAD=1` is set **and** `--verbose` or `--debug` is active, the CLI prints resolved `.env` sources in order of precedence.

```console
[.env resolution]
  ✅ Loaded: .env.override
  ✅ Loaded: .env
  ⚠️  Skipped: .env.local (not found)
  ✅ Active: logs/DEV/myproject.log
```


The output might look like:

```txt
[env] Loading settings...
[env] Using .env.override (committed override)
[debug] CLI args:
Namespace(query='foo', debug=True, ...)

[debug] Settings:
Settings(env='DEV', log_level='DEBUG', ...)
```

This is implemented in:

```python
print_dotenv_debug(settings, debug=args.debug, use_color=use_color)
```

It formats results with optional ANSI color codes and ensures clarity for devs.

---

## 🧪 Debug Output in Tests

Enabling `--debug`:

* Activates `DEBUG` level for both console and file logs
* Triggers `.env` diagnostics (if `MYPROJECT_DEBUG_ENV_LOAD=1`)
* Calls `print_debug_diagnostics()` for full config visibility

### Sample Output:

```json
{
  "environment": "DEV",
  "dotenv_path": ".env.override",
  "log_dir": "logs/DEV",
  "color": "auto",
  "verbose": true,
  "debug": true
}
```

Function:

```python
print_debug_diagnostics(args, settings, use_color=True)
```

### Unit Tests


The test suite ensures diagnostics behave predictably:

* Tests use `log_stream` to capture debug output
* `print_dotenv_debug()` is explicitly tested in `test_settings.py`
* CLI integration tests simulate `--debug` and assert diagnostic stdout
* `PYTEST_CURRENT_TEST` automatically enables `.env.test` loading

### Example Test Assertion

```python
assert "[debug] CLI args" in result.stdout
assert "[debug] Settings:" in result.stdout
```

* `tests/cli/test_cli_main.py` covers:

  * `--debug` output structure
  * Behavior with and without `MYPROJECT_DEBUG_ENV_LOAD=1`
  * Coloring logic with `--color=never`

* Fixtures:

  * `log_stream` to capture stdout
  * `patch_env` to set or unset debug-related variables

These ensure full coverage without leaking logs or polluting test output.



---

## 📦 Implementation Details

All diagnostic functions live in `cli/diagnostics.py`:

* `print_dotenv_debug(settings, debug: bool, use_color: bool)`
* `print_debug_diagnostics(args, settings, use_color: bool)`

These functions:

* Use `json.dumps(..., indent=2)` for structured output
* Route only to `stdout` to avoid interfering with stderr
* Are guarded by clear conditional checks (no accidental prints)
* Are fully color-aware (fallback if `--no-color`)

---


---

## 🔗 Related

* Environment behavior and dotenv loading: [env-logging-scenarios.md](env-logging-scenarios.md)
* CLI architecture and diagnostics: [cli\_architecture.md](cli_architecture.md)
* Logging integration: [logging\_system.md](logging_system.md)
* Settings system: [environment\_config.md](environment_config.md)
---

## ✅ Summary

The debug and diagnostics system in `myproject` is rich yet unobtrusive. It cleanly separates logic from output, is safe to enable in production, and provides full visibility for debugging without breaking flow. All diagnostics are tested and color-aware, making them suitable for local, CI, or advanced debugging.
