.PHONY: help install develop lint format format-check test test-single test-fast coverage coverage-xml check-all \
        precommit precommit-run precommit-check build clean clean-pyc publish publish-test upload-coverage

# -------------------------------------------------------------------
# Help
# -------------------------------------------------------------------
help:
	@echo "Available Makefile commands:"
	@echo "  install             Install the package in editable mode"
	@echo "  develop             Install with all dev dependencies"
	@echo "  lint                Run Ruff and MyPy for static analysis"
	@echo "  format              Auto-format using Ruff"
	@echo "  format-check        Check formatting (dry run)"
	@echo "  test                Run all tests using Pytest"
	@echo "  test-single         Run a single test file or keyword with TEST=..."
	@echo "  test-fast           Run only last failed tests"
	@echo "  coverage            Run tests with terminal coverage report"
	@echo "  coverage-xml        Generate XML coverage (for CI or Coveralls)"
	@echo "  check-all           Run format-check, lint, and full test suite"
	@echo "  precommit           Install pre-commit hook"
	@echo "  precommit-check     Dry run pre-commit hook"
	@echo "  precommit-run       Run all pre-commit hooks"
	@echo "  build               Build package for distribution"
	@echo "  clean               Remove build artifacts"
	@echo "  clean-pyc           Remove __pycache__ and .pyc files"
	@echo "  publish-test        Upload to TestPyPI"
	@echo "  publish             Upload to PyPI"
	@echo "  upload-coverage     Upload coverage to Coveralls"

# -------------------------------------------------------------------
# Install & Development
# -------------------------------------------------------------------
install:
	pip install -e .

develop:
	pip install -e .[dev]

# -------------------------------------------------------------------
# Linting & Formatting
# -------------------------------------------------------------------
lint:
	ruff check src/ tests/
	mypy src/ tests/

format:
	ruff format src/ tests/

format-check:
	ruff format --check src/ tests/

# -------------------------------------------------------------------
# Testing
# -------------------------------------------------------------------
test:
	pytest tests/ -v

test-single:
	pytest $(TEST) -v

test-fast:
	pytest --lf -x -v

coverage:
	pytest --cov=myproject --cov-report=term

coverage-xml:
	pytest --cov=myproject --cov-report=term --cov-report=xml

check-all: format-check lint coverage

# -------------------------------------------------------------------
# Pre-commit Hooks
# -------------------------------------------------------------------
precommit:
	pre-commit install

precommit-check:
	pre-commit run --all-files --hook-stage manual --verbose --show-diff-on-failure --color always --config .pre-commit-config.yaml

precommit-run:
	pre-commit run --all-files

# -------------------------------------------------------------------
# Build & Distribution
# -------------------------------------------------------------------
build:
	python -m build

clean:
	python -c "import shutil, glob; [shutil.rmtree(p, ignore_errors=True) for p in ['dist', 'build'] + glob.glob('*.egg-info')]"

clean-pyc:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +

publish-test:
	twine upload --repository testpypi dist/*

publish:
	twine check dist/*
	twine upload dist/*

upload-coverage:
	coveralls
