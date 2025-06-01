.PHONY: help install develop lint format format-check test test-file test-fast \
        test-coverage test-coverage-xml show-coverage show-coverage-file clean-coverage \
        check-all test-cov-html test-watch \
        precommit precommit-run precommit-check \
        env-check env-debug dotenv-debug \
        safety check-updates \
        build clean clean-pyc clean-all \
        publish publish-test upload-coverage

# -------------------------------------------------------------------
# Help
# -------------------------------------------------------------------
help:
	@echo "Available Makefile commands:"
	@echo "  install                Install the package in editable mode"
	@echo "  develop                Install with all dev dependencies"
	@echo "  lint                   Run Ruff and MyPy for static analysis"
	@echo "  format                 Auto-format using Ruff"
	@echo "  format-check           Check formatting (dry run)"
	@echo "  test                   Run all tests using Pytest"
	@echo "  test-file              Run a single test file or keyword with FILE=... (e.g. make test-file FILE=tests/test_cli.py)"
	@echo "  test-fast              Run only last failed tests"
	@echo "  test-coverage          Run tests and show terminal coverage summary"
	@echo "  test-coverage-xml      Run tests and generate XML coverage report"
	@echo "  show-coverage          Show full line-by-line coverage report"
	@echo "  show-coverage-file     Show coverage for a specific file: FILE=... (e.g. make show-coverage-file FILE=src/myproject/cli/main.py)"
	@echo "  clean-coverage         Erase cached coverage data"
	@echo "  test-cov-html          Run tests with HTML coverage report and open it"
	@echo "  test-watch             Auto-rerun tests on file changes"
	@echo "  check-all              Run format-check, lint, and full test suite"
	@echo "  precommit              Install pre-commit hook"
	@echo "  precommit-check        Dry run pre-commit hook"
	@echo "  precommit-run          Run all pre-commit hooks"
	@echo "  env-check              Show Python, virtualenv, and environment info"
	@echo "  env-debug              Show debug-related environment info"
	@echo "  dotenv-debug           Print dotenv loading debug info"
	@echo "  safety                 Run dependency vulnerability check"
	@echo "  check-updates          List outdated pip packages"
	@echo "  build                  Build package for distribution"
	@echo "  clean                  Remove build artifacts"
	@echo "  clean-pyc              Remove __pycache__ and .pyc files"
	@echo "  clean-all              Remove all caches, logs, coverage, etc."
	@echo "  publish-test           Upload to TestPyPI"
	@echo "  publish                Upload to PyPI"
	@echo "  upload-coverage        Upload coverage to Coveralls"

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

test-file:
	pytest $(FILE) -v

test-fast:
	pytest --lf -x -v

test-coverage:
	pytest --cov=myproject --cov-report=term

test-coverage-xml:
	pytest --cov=myproject --cov-report=term --cov-report=xml

test-cov-html:
	pytest --cov=myproject --cov-report=html
ifeq ($(OS),Windows_NT)
	start htmlcov\index.html
else
	open htmlcov/index.html
endif


show-coverage:
	coverage report -m

show-coverage-file:
ifeq ($(FILE),)
	@echo "Usage: make show-coverage-file FILE=path/to/file.py"
	@exit 1
else
	coverage report -m $(FILE)
endif

clean-coverage:
	coverage erase

check-all: format-check lint test-coverage

test-watch:
	ptw --runner "pytest -v" tests/

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
# Environment & Debugging
# -------------------------------------------------------------------
env-check:
	@echo "Python: $$(python --version)"
	@echo "Virtualenv: $$(which python)"
	@echo "Environment: $${MYPROJECT_ENV:-not set}"

env-debug:
	@echo "Debug: $${MYPROJECT_DEBUG_ENV_LOAD:-not set}"

dotenv-debug:
	python -c "from myproject.settings import print_dotenv_debug; print_dotenv_debug()"

# -------------------------------------------------------------------
# Security & Dependency Management
# -------------------------------------------------------------------
safety:
	safety scan

check-updates:
	pip list --outdated

# -------------------------------------------------------------------
# Build & Distribution
# -------------------------------------------------------------------
build:
	python -m build

clean:
	python -c "import shutil, glob; [shutil.rmtree(p, ignore_errors=True) for p in ['dist', 'build'] + glob.glob('*.egg-info')]"

clean-pyc:
	python -c "import pathlib, shutil; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"

clean-all: clean clean-pyc
	python -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.log')]"
	python -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in map(pathlib.Path, ['.pytest_cache', '.mypy_cache', '.ruff_cache', 'htmlcov']) if p.exists()]"
	python -c "import pathlib; [p.unlink() for p in map(pathlib.Path, ['.coverage', 'coverage.xml']) if p.exists()]"


publish-test:
	twine upload --repository testpypi dist/*

publish:
	twine check dist/*
	twine upload dist/*

upload-coverage:
	coveralls
