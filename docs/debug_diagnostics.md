# 🛠️ Diagnostics & Debug Output

This document explains the internal diagnostics and debug features implemented in the `myproject` CLI. These tools aid development, troubleshooting, and configuration transparency.

---

## 📚 Table of Contents

* [🧭 Overview](#-overview)
* [🔍 Diagnostic Controls](#-diagnostic-controls)
* [⚙️ Dotenv Debug Output](#-dotenv-debug-output)
* [🧠 Full Debug Mode](#-full-debug-mode)
* [📦 Implementation Details](#-implementation-details)
* [🧪 Testing Diagnostics](#-testing-diagnostics)
* [🔗 Related](#-related)
* [✅ Summary](#-summary)

---

## 🧭 Overview

The CLI includes built-in diagnostic output to:

* Reveal how environment variables are resolved
* Print active settings after parsing and loading
* Aid debugging during development or CI/CD
* Ensure that `.env` resolution and logging setup are traceable

These outputs are tightly integrated with `--debug`, `--verbose`, and the `MYPROJECT_DEBUG_ENV_LOAD` environment variable.

---

## 🔍 Diagnostic Controls

| Trigger                      | Output Scope                                 | When to Use                               |
| ---------------------------- | -------------------------------------------- | ----------------------------------------- |
| `--debug`                    | Full diagnostics + DEBUG logging             | CLI development, troubleshooting          |
| `--verbose`                  | INFO-level output to stdout                  | Basic inspection of CLI processing        |
| `MYPROJECT_DEBUG_ENV_LOAD=1` | Prints resolved `.env` sources and locations | Investigate which dotenv files are loaded |

All debug output is written to stdout (not stderr) and respects the `--color` flag.

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

This is implemented in:

```python
print_dotenv_debug(settings, debug=args.debug, use_color=use_color)
```

It formats results with optional ANSI color codes and ensures clarity for devs.

---

## 🧠 Full Debug Mode

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

## 🧪 Testing Diagnostics

* `tests/cli/test_cli_main.py` covers:

  * `--debug` output structure
  * Behavior with and without `MYPROJECT_DEBUG_ENV_LOAD=1`
  * Coloring logic with `--color=never`

* Fixtures:

  * `log_stream` to capture stdout
  * `patch_env` to set or unset debug-related variables

These ensure full coverage without leaking logs or polluting test output.

---

## 🔗 Related

* [Logging System](logging_system.md)
* [Environment Config](environment_config.md)
* [CLI Architecture](cli_architecture.md)

---

## ✅ Summary

Diagnostics are first-class citizens in `myproject`. With rich debug output, color support, and full test coverage, developers can easily inspect config resolution, runtime state, and CLI behavior in any environment.
