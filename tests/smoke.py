#!/usr/bin/env python3
"""Smoke tests for verifying installation and CLI functionality."""

import importlib
import subprocess
import sys
import tomllib
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run a command and return the completed process. Raises on error."""
    # Using check=True to automatically raise CalledProcessError on non-zero exit codes.
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def get_package_name() -> str:
    """Get package name from pyproject.toml."""
    # Assumes Python 3.11+ for tomllib
    current_path = Path(__file__).resolve().parent
    while current_path != current_path.parent:
        pyproject_path = current_path / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            return data["project"]["name"]
        current_path = current_path.parent
    raise RuntimeError("Could not find pyproject.toml in parent directories.")


def test_version(cmd: list[str]) -> None:
    """Test --version option works."""
    result = run([*cmd, "--version"])
    version = result.stdout.strip()
    assert version, "version output empty"
    print(f"✓ version: {version}")


def test_help(cmd: list[str]) -> None:
    """Test help command works."""
    result = run([*cmd, "--help"])
    out = result.stdout
    assert "deconstruct" in out, "missing deconstruct command"
    assert "reconstruct" in out, "missing reconstruct command"
    print("✓ help")


def test_module_invocation() -> None:
    """Test python -m <package> works."""
    package = get_package_name()
    result = run([sys.executable, "-m", package, "--version"])
    version = result.stdout.strip()
    assert version, "module version output empty"
    print(f"✓ python -m {package} --version: {version}")


def test_imports() -> None:
    """Test package imports work correctly."""
    package = get_package_name()

    # Test main package imports
    pkg = importlib.import_module(package)
    assert hasattr(pkg, "BIP39")
    assert hasattr(pkg, "SLIP39")
    assert hasattr(pkg, "__version__")
    assert pkg.__version__, "version is empty"

    # Test submodule imports
    tools_module = importlib.import_module(f"{package}.tools")
    assert hasattr(tools_module, "BIP39")

    cli_module = importlib.import_module(f"{package}.cli")
    assert hasattr(cli_module, "app")
    assert hasattr(cli_module, "deconstruct")
    assert hasattr(cli_module, "reconstruct")

    print(f"✓ imports: BIP39, SLIP39, __version__={pkg.__version__}")


def main() -> None:
    """Run smoke tests."""
    # Command can be passed as args (e.g., "./binary" or "package")
    package = get_package_name()
    cmd = sys.argv[1:] if len(sys.argv) > 1 else [str(package)]

    print(f"Running smoke tests with: {' '.join(cmd)}")
    try:
        # Always run import and module tests (package-level verification)
        test_imports()
        test_module_invocation()

        # Run CLI tests with provided command
        test_version(cmd)
        test_help(cmd)
        print("All smoke tests passed!")
    except (subprocess.CalledProcessError, AssertionError) as e:
        print("\nSmoke test failed!", file=sys.stderr)
        if isinstance(e, subprocess.CalledProcessError):
            print(
                f"Command '{' '.join(e.cmd)}' failed with exit code {e.returncode}.",
                file=sys.stderr,
            )
            if e.stderr:
                print(f"Stderr:\n{e.stderr.strip()}", file=sys.stderr)
        else:
            print(f"Assertion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
