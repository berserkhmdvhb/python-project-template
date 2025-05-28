.PHONY: help install develop lint format test test-fast coverage coverage-xml check-all \
        precommit precommit-run build clean

help:
	@echo "Available Makefile commands:"
	@echo "  install            Install the package in editable mode"
	@echo "  develop            Install with all dev dependencies"
	@echo "  lint               Run Ruff and MyPy for static analysis"
	@echo "  format             Format code using Ruff"
	@echo "  test               Run all tests using Pytest"
	@echo "  test-fast          Run only last failed tests"
	@echo "  coverage           Run tests with terminal coverage report"
	@echo "  coverage-xml       Generate XML coverage (for CI or Coveralls)"
	@echo "  check-all          Run format, lint, and full test suite"
	@echo "  precommit          Install pre-commit hook"
	@echo "  precommit-run      Run all pre-commit hooks"
	@echo "  build              Build package for distribution"
	@echo "  clean              Remove build artifacts"

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

test-fast:
	pytest --lf -x -v

coverage:
	pytest --cov=myproject --cov-report=term

coverage-xml:
	pytest --cov=myproject --cov-report=term --cov-report=xml

check-all: format lint coverage

precommit:
	pre-commit install

precommit-run:
	pre-commit run --all-files

build:
	python -m build

clean:
	python -c "import shutil, glob; [shutil.rmtree(p, ignore_errors=True) for p in ['dist', 'build'] + glob.glob('*.egg-info')]"
