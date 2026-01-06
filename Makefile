NAME := $(shell basename $(CURDIR))

.PHONY: lint format smoke test cov build clean qr help all

help:
	@echo "Available targets:"
	@echo "  lint   - Run ruff linter and formatter check"
	@echo "  format - Run ruff formatter"
	@echo "  smoke  - Run smoke tests"
	@echo "  test   - Run tests with pytest"
	@echo "  cov    - Run tests with pytest and coverage"
	@echo "  build  - Build binary with Nuitka"
	@echo "  qr     - Generate QR codes for donation addresses"
	@echo "  clean  - Remove build artifacts"
	@echo "  all    - Run lint, test, and build"

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check . --fix
	uv run ruff format .

test:
	uv run python -m pytest

smoke:
	uv run python tests/smoke.py $(NAME)

cov:
	uv run python -m pytest --cov --cov-report=term-missing --cov-fail-under=90

build:
	./scripts/build.sh

qr:
	uv run python scripts/qr.py

clean:
	rm -rf cli.dist/ dist/ build/ *.egg-info/ .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

all: build smoke cov qr format
