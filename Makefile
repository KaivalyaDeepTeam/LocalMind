# LocalMind Makefile
# Developer convenience commands for testing, linting, and building

.PHONY: help test test-fast test-unit test-integration lint format typecheck security coverage all clean install install-dev

# Default target
help:
	@echo "LocalMind Development Commands"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run full test suite with coverage"
	@echo "  make test-fast       Run unit tests only (quick)"
	@echo "  make test-unit       Run unit tests with verbose output"
	@echo "  make test-integration Run integration tests only"
	@echo "  make coverage        Generate HTML coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Check code with ruff"
	@echo "  make format          Format code with ruff"
	@echo "  make typecheck       Run mypy type checking"
	@echo "  make security        Run bandit security scan"
	@echo ""
	@echo "Development:"
	@echo "  make install         Install package"
	@echo "  make install-dev     Install with dev dependencies"
	@echo "  make all             Run format, lint, typecheck, and test"
	@echo "  make clean           Remove build artifacts"
	@echo ""
	@echo "Pre-commit:"
	@echo "  make pre-commit-install  Install pre-commit hooks"
	@echo "  make pre-commit-run      Run pre-commit on all files"

# Testing targets
test:
	pytest tests/ -v --cov=localmind --cov-report=term-missing

test-fast:
	pytest tests/unit/ -x -q --tb=short

test-unit:
	pytest tests/unit/ -v --tb=short

test-integration:
	pytest tests/integration/ -v --tb=short

coverage:
	pytest tests/ --cov=localmind --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

# Code quality targets
lint:
	ruff check localmind/ tests/

format:
	ruff format localmind/ tests/
	ruff check --fix localmind/ tests/

typecheck:
	mypy localmind/ --ignore-missing-imports --no-strict-optional

security:
	bandit -r localmind/ -ll --skip B101

# Combined targets
all: format lint typecheck test

check: lint typecheck security

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

# Pre-commit targets
pre-commit-install:
	pre-commit install

pre-commit-run:
	pre-commit run --all-files

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# CI/CD specific targets
ci-test:
	pytest tests/ --cov=localmind --cov-fail-under=60 --cov-report=xml

ci-lint:
	ruff check localmind/ tests/ --output-format=github

ci-security:
	bandit -r localmind/ -ll --skip B101 -f json -o bandit-report.json || true
