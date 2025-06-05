# 🧠 Core Logic

This document outlines the internal logic, responsibilities, and design principles of `myproject.core`, which contains the core processing functions used by both the CLI and external consumers.

---

## 📚 Table of Contents

* [🔍 Purpose](#-purpose)
* [📦 Location and Interface](#-location-and-interface)
* [🧱 Design Principles](#-design-principles)
* [⚙️ Implementation Details](#-implementation-details)
* [🧪 Testing Strategy](#-testing-strategy)
* [🔗 CLI Integration](#-cli-integration)
* [✅ Summary](#-summary)

---

## 🔍 Purpose

The `core.py` module encapsulates the core logic of the application. Its goal is to provide clean, pure, and reusable functions that:

* Perform the main business logic (e.g., processing user queries)
* Remain independent of CLI concerns (arguments, output, logging)
* Are easy to test, debug, and import in other contexts

---

## 📦 Location and Interface

```
src/myproject/
├── core.py          # Core logic module
```

The module typically exposes one or more main entry-point functions:

```python
# core.py
def process_query(query: str) -> dict:
    ...
```

---

## 🧱 Design Principles

1. **Purity**

   * Functions avoid side effects (e.g., no logging, no I/O)
   * Operate solely on input arguments and return values

2. **Reusability**

   * Core functions can be used in scripts, APIs, or UIs

3. **Decoupling**

   * No dependencies on CLI or environment logic
   * Does not import from `cli/`, `settings`, or `.env` logic

4. **Type Safety**

   * Fully typed function signatures using Python type hints

5. **Testability**

   * Functions are easily testable in isolation without mocks or patches

---

## ⚙️ Implementation Details

### 🔹 `process_query(query: str) -> dict`

This is the main business logic entry point. It performs some form of transformation on the input query and returns a structured dictionary result.

#### Example:

```python
def process_query(query: str) -> dict:
    return {
        "input": query,
        "output": query.upper(),
    }
```

In real applications, this could perform text analysis, call external services, query databases, or apply domain logic.

#### Output Format:

All results follow a standard dictionary format, enabling both JSON and text rendering in the CLI:

```json
{
  "input": "hello",
  "output": "HELLO"
}
```

---

## 🧪 Testing Strategy

All core logic is tested independently in `tests/test_core.py`.

* Full unit tests with varied inputs and edge cases
* Test without patching or environment mocking
* High coverage (100%) due to simplicity and isolation

#### Example:

```python
def test_process_query_uppercase():
    result = process_query("test")
    assert result == {"input": "test", "output": "TEST"}
```

---

## 🔗 CLI Integration

The CLI layer (`handlers.py`) calls `core.process_query()` after parsing arguments and setting up configuration.

This ensures:

* Logic is reusable outside the CLI
* Separation of concerns: CLI handles UX, `core` handles business logic
* Easy migration of logic to a web API, job runner, or other interface

---

## ✅ Summary

The `core.py` module defines the core logic for query handling. It is pure, reusable, and fully tested. It plays a central role in the application's architecture by decoupling logic from interface concerns and enabling test-driven development from day one.
