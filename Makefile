.PHONY: help install develop lint format test check-all

help:
	@echo "Available Makefile commands:"
	@echo "  install         Install the package in editable mode"
	@echo "  develop         Install package with all dev dependencies"
	@echo "  lint            Run Ruff and MyPy for static analysis"
	@echo "  format          Format code using Ruff"
	@echo "  test            Run all tests using Pytest"
	@echo "  check-all       Run format, lint, and test (CI-friendly)"

install:
	pip install -e .

develop:
	pip install -e .[dev]

lint:
	ruff check src/ tests/
	mypy src/ tests/

format:
	ruff format src/ tests/

test:
	pytest tests/ -v

check-all: format lint test
