# AGENTS.md

## Overview

This repo is a Python CLI tool (`interstellar/`) for managing cryptocurrency mnemonics using BIP39 and SLIP39 standards — including generation, splitting, reconstruction, and Shamir secret sharing.

## CI Checks

All changes must pass these checks before merging (runs on ubuntu, macOS, and Windows):

```bash
make lint      # ruff check . && ruff format --check .
make type      # ty check src tests
make cov       # pytest with coverage (threshold enforced)
```

## Running Checks Locally

```bash
make ci DEV=1          # install deps (frozen lockfile, requires uv)
make lint              # lint + format check
make type              # type check (ty)
make test              # unit tests only
make cov               # unit tests with coverage
make smoke             # smoke tests (tests/smoke.py)
make format            # auto-fix lint + format
```

## Project Structure

- `src/interstellar/` — core CLI module (BIP39, SLIP39, CLI app)
- `tests/` — pytest unit tests and smoke tests
- `scripts/` — utility scripts (build, QR codes)
- `pyproject.toml` — project config, dependencies, and tool settings
- `Makefile` — build/test/lint commands

## Key Conventions

- **Package manager**: `uv` (all commands run via `uv run`)
- **Type checker**: `ty` (astral, not mypy)
- **Linter/Formatter**: `ruff`
- **Test runner**: `pytest` with `pytest-xdist` (`-n auto`) and `pytest-cov`
- **Python version**: 3.13
