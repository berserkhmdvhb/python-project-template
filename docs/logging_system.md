# 📝 Logging System

This document describes the structured logging system used in the `myproject` template. It is designed to be modular, environment-aware, and fully testable.

---

## 📚 Table of Contents

* [🧭 Overview](#-overview)
* [🗂️ Files Involved](#-files-involved)
* [📂 Log Directory Structure](#-log-directory-structure)
* [⚙️ Logging Behavior](#-logging-behavior)
* [🔁 Log Rotation](#-log-rotation)
* [📥 CLI Logging Options](#-cli-logging-options)
* [🧪 Logging in Tests](#-logging-in-tests)
* [🔗 Related](#-related)
* [✅ Summary](#-summary)


---

## 🧭 Overview

Logging in `myproject` is designed to:

* Be isolated per environment (DEV, UAT, PROD, TEST)
* Allow fine-grained control over verbosity and debug output
* Store persistent log files in organized folders
* Rotate logs using `RotatingFileHandler`
* Integrate cleanly with CLI options like `--verbose`, `--debug`, and `--env`

---

## 🗂️ Files Involved

| File              | Responsibility                                   |
| ----------------- | ------------------------------------------------ |
| `logger_utils.py` | Create and configure loggers, handlers, formats  |
| `cli_main.py`     | Triggers `setup_logging()` based on parsed args  |
| `settings.py`     | Provides env-aware config for log folder & level |
| `utils_logger.py` | Shared helpers and file-level logger instance    |

---

## 📂 Log Directory Structure

Logs are stored under a per-environment folder inside `logs/`:

```bash
logs/
├── DEV/
│   └── myproject.log
├── PROD/
│   └── myproject.log
├── TEST/
│   └── myproject.log
```

This is determined dynamically by:

```python
log_dir = ROOT / "logs" / settings.environment
```

You can override log paths or rotate behavior via environment variables in `.env` files.

---

## ⚙️ Logging Behavior

* Log level defaults to `INFO` in most environments
* Level switches to `DEBUG` if:

  * `--debug` is passed
  * `MYPROJECT_DEBUG_ENV_LOAD=1` is set

### Logging Targets

* **Console Handler**:

  * Active only if `--verbose` or `--debug` is used
  * Colored output if `--color` is enabled or `isatty()` detects it

* **File Handler**:

  * Always active unless `settings.disable_logging` is true
  * Uses a rotating handler (see below)
  * Filename: `myproject.log` in correct folder


#### Setup Function: `setup_logging()`


```python
def setup_logging(env: str, verbose: bool, debug: bool, reset: bool = False) -> None:
```

### 🔹 Purpose

Initializes the logging system with proper handlers and format, depending on the environment and verbosity.

**🔹 Behavior**

* **Environment-based folder**: Logs go to `logs/{env}/myproject.log`.
* **Reset control**: Removes previous handlers if `reset=True`.
* **Verbose flag**:

  * If `True`, logs to console using a `StreamHandler` with colored output (when supported).
* **Debug flag**:

  * Enables `DEBUG` level output.
  * Otherwise, uses `INFO` or `WARNING`.

**🔹 Logging Levels**

| Flag        | Console Level | File Level |
| ----------- | ------------- | ---------- |
| `--verbose` | `INFO`        | `INFO`     |
| `--debug`   | `DEBUG`       | `DEBUG`    |
| None        | Silent        | `WARNING`  |
---

#### Teardown Function: `teardown_logger()`

```python
def teardown_logger() -> None:
```


**🔹 Purpose**

Cleans up any handlers from the root logger. Prevents duplicate log entries when multiple CLI runs occur within the same process (e.g. during testing).

**🔹 Behavior**

* Iterates through existing handlers.
* Calls `.close()` and removes each handler.
* Resets the logger to a clean state.

This is especially useful during test teardown and subprocess simulation.

## 🔁 Log Rotation

Implemented via `logging.handlers.RotatingFileHandler`, with size and backup behavior controlled by:

```env
MYPROJECT_LOG_MAX_BYTES=1000000
MYPROJECT_LOG_BACKUP_COUNT=3
```

The file is rotated when `maxBytes` is exceeded. Old files are preserved up to `backupCount`.

```python
handler = RotatingFileHandler(
    log_path,
    maxBytes=MAX_BYTES,
    backupCount=BACKUP_COUNT,
)
```

Dfeault Rotation uses a suffix `.1`, `.2`, etc., and overwrites old files in a cyclic manner.
E.g., `info.log.1`, `info.log.2`

#### Custom Handler: `CustomRotatingFileHandler`

This subclass of `RotatingFileHandler` was added for customization, which has the following:

* Consistent rotation filenames (removes timestamp junk)
* Cross-platform-safe path logic
* Custom `get_files_to_delete()` to enforce max backups properly


**🔹 Rotation Logic**

Rotation is size-based (default from `.env`, e.g. 1 MB). Once full:

* Moves current log to `.log.1`, `.log.2`, etc.
* Deletes oldest log if exceeding `backupCount`

**🔹 Why Custom?**

Python’s `RotatingFileHandler` has inconsistent filename behavior across OSes. This subclass ensures:

* Cleaner log file naming
* Predictable test behavior
* Control over deletion policy

---

## 📥 CLI Logging Options

| Option       | Behavior                                                             |
| ------------ | -------------------------------------------------------------------- |
| `--verbose`  | Enables stdout logging (INFO level)                                  |
| `--debug`    | Enables stdout + file logging (DEBUG level) and internal diagnostics |
| `--env`      | Changes logging folder and base config                               |
| `--no-color` | Disables ANSI color codes                                            |

These are parsed and passed to `setup_logging()` inside `cli_main.py`.

---

## 🧪 Logging in Tests

* Tests isolate log folders to avoid real log pollution
* `log_stream` fixture captures in-memory logs for inspection
* `clean_myproject_logger` resets handlers between test runs
* CLI logging is tested via subprocess with temp folders

You can fully simulate logging behavior in tests without writing to disk by combining `log_stream` and mocking file handlers.


When the CLI or tests run under `PYTEST_CURRENT_TEST` or use the `--env test` flag:

* Logging still initializes
* Output is isolated to `logs/TEST/`
* `teardown_logger()` is invoked in `conftest.py` to reset after each test

This guarantees that tests don’t leak logs between runs.


---

## 🔗 Related

* Full environment and `.env` logic: [docs/env-logging-scenarios.md](env-logging-scenarios.md)
* Settings loader implementation: [environment\_config.md](environment_config.md)
* CLI architecture and logging integration: [cli\_architecture.md](cli_architecture.md)


---

## ✅ Summary

The logging system in `myproject` is flexible, isolated, and test-friendly. It supports rotation, per-env folders, and full CLI integration with minimal setup. It is designed for real-world applications and production-readiness out of the box.
