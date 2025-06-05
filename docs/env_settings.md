# 🧩 Environment Settings (`settings.py`)

This document provides a detailed overview of the environment configuration logic in `myproject`, focusing on the behavior of `settings.py` and how it manages variables, environments, `.env` files, and test scenarios.

---

## 📚 Table of Contents

* [🔍 Purpose](#-purpose)
* [📄 Environment Detection](#-environment-detection)
* [📁 .env File Prioritization](#-env-file-prioritization)
* [🧠 Implementation Details](#-implementation-details)
* [🧪 Test Mode Behavior](#-test-mode-behavior)
* [🐛 Debugging Tools](#-debugging-tools)
* [📦 Environment Variables Reference](#-environment-variables-reference)
* [🧰 Usage Examples](#-usage-examples)
* [✅ Summary](#-summary)

---

## 🔍 Purpose

The `settings.py` module is responsible for:

* Centralized access to environment variables
* Structured loading from `.env` files
* Supporting manual overrides via CLI flags
* Providing fallback behavior in CI and test environments
* Debugging visibility into config resolution

---

## 📄 Environment Detection

By default, `myproject` supports four named environments:

* `DEV`: Development
* `UAT`: User Acceptance Testing
* `PROD`: Production
* `TEST`: Testing mode (used by pytest)

The environment is determined by the following (in priority order):

1. CLI argument `--env`
2. Environment variable `MYPROJECT_ENV`
3. Defaults to `DEV`

The logic is designed to be minimal and consistent across CLI, library, and test execution.

---

## 📁 .env File Prioritization

`.env` file selection is critical for predictable config behavior. The following table shows the full priority chain:

| Priority | File            | Loaded When                   | Purpose / Use Case                                               | Committed to Git? | Override Others?   |
| -------- | --------------- | ----------------------------- | ---------------------------------------------------------------- | ----------------- | ------------------ |
| 1️⃣      | `DOTENV_PATH`   | Set via environment variable  | Force a custom env file at runtime (e.g. for advanced CLI usage) | ❌ (user-defined)  | ✅                  |
| 2️⃣      | `.env.override` | Exists in project root        | Enforced values (CI/CD, production)                              | ✅                 | ✅                  |
| 3️⃣      | `.env`          | Exists in project root        | Main team-shared configuration                                   | ✅                 | ✅ (if no override) |
| 4️⃣      | `.env.local`    | Exists in project root        | Developer-specific overrides (not shared)                        | ❌ (`.gitignore`)  | ✅ (over `.env`)    |
| 5️⃣      | `.env.test`     | Running under `pytest`        | Clean isolation for tests                                        | ✅ (optional)      | ✅ (in test mode)   |
| 6️⃣      | `.env.sample`   | None of the above are present | Documentation or last-resort fallback                            | ✅                 | 🚫                 |
File resolution happens once and is cached to avoid repeated loading.

For a comprehensive walkthrough of how these environment layers interact — including practical CLI scenarios, .env overrides, logging folder behaviors, and test-specific behavior — refer to [docs/env-logging-scenarios.md](https://github.com/berserkhmdvhb/python-project-template/blob/main/docs/env-logging-scenarios.md). 

---

## 🧠 Implementation Details

The `load_settings()` function uses the `dotenv_values()` loader and a controlled override strategy.

```python
from dotenv import dotenv_values

if TEST_MODE and TEST_ENV_PATH.exists():
    env_vars.update(dotenv_values(TEST_ENV_PATH))

elif DOTENV_PATH:
    env_vars.update(dotenv_values(DOTENV_PATH))
```

Highlights:

* Environment is normalized (`.strip().upper()`)
* If `PYTEST_CURRENT_TEST` is present, test mode is enforced
* A warning is logged if `DOTENV_PATH` is provided but missing
* All resolved env vars are stored in a singleton `Settings` object for consistency
* `.env.sample` is used only if no other file was loaded

> The `Settings` object is frozen (via `@dataclass(frozen=True)`) to ensure immutability once loaded.

---

## 🧪 Test Mode Behavior

When the environment variable `PYTEST_CURRENT_TEST` is detected, the environment is auto-set to `TEST` and the following happens:

* `.env.test` is preferred over all other `.env` files
* Logging is silenced unless explicitly overridden
* Some CLI logic switches to simulation mode (e.g., `handlers.py`)

This ensures full test isolation.

---

## 🐛 Debugging Tools

The environment layer supports two main debug modes:

### `MYPROJECT_DEBUG_ENV_LOAD=1`

Prints detailed information about:

* Which `.env` file was selected
* What environment is active
* Which variables were set and their values (partially redacted)

To activate:

```bash
MYPROJECT_DEBUG_ENV_LOAD=1 myproject --env uat
```

Or via Makefile:

```bash
make dotenv-debug
```

### `--debug` CLI Flag

Triggers additional diagnostics in the CLI including:

* Settings dump
* Output format config
* Explicit log file locations

---

## 📦 Environment Variables Reference

| Variable                   | Description                        | Example           |
| -------------------------- | ---------------------------------- | ----------------- |
| `MYPROJECT_ENV`            | Current environment name           | `DEV`, `PROD`     |
| `DOTENV_PATH`              | Override `.env` file path manually | `./.env.override` |
| `MYPROJECT_LOG_DIR`        | Base directory for logs            | `./logs/`         |
| `MYPROJECT_LOG_MAX_BYTES`  | Max log file size in bytes         | `1048576`         |
| `MYPROJECT_LOG_BACKUPS`    | Number of rotated log backups      | `5`               |
| `MYPROJECT_DEBUG_ENV_LOAD` | Print env resolution info          | `0` or `1`        |

---

## 🧰 Usage Examples

### Example 1: Load from custom `.env`

```bash
DOTENV_PATH=secrets/.env.prod myproject --query "status"
```

### Example 2: Test mode behavior

```bash
PYTEST_CURRENT_TEST=1 pytest tests/
# Will load .env.test and use TEST environment
```

### Example 3: Diagnostic debug output

```bash
MYPROJECT_DEBUG_ENV_LOAD=1 myproject --env uat
```

### Example 4: CLI overrides default

```bash
myproject --env prod --dotenv-path ./envs/prod.env
```

---

## ✅ Summary

`settings.py` is the heart of configuration management for `myproject`. It enables deterministic behavior across environments, respects CLI overrides, and integrates smoothly with test infrastructure. Its debug modes and `.env` resolution logic ensure full transparency and control for developers and CI pipelines alike.
