#!/usr/bin/env python3
"""Smoke tests for verifying installation and CLI functionality."""

import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run a command and return the completed process. Raises on error."""
    # Using check=True to automatically raise CalledProcessError on non-zero exit codes.
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def get_package_name() -> str:
    """Get package name from directory structure."""
    return Path(__file__).resolve().parts[-3]


def test_version(cmd: list[str]) -> None:
    """Test version command works."""
    result = run([*cmd, "version"])
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
    result = run([sys.executable, "-m", package, "version"])
    version = result.stdout.strip()
    assert version, "module version output empty"
    print(f"✓ python -m {package} version: {version}")


def test_imports() -> None:
    """Test package imports work correctly."""
    package = get_package_name()
    # Use exec to dynamically import based on package name
    exec_globals: dict = {}

    # Test main package imports
    exec(f"from {package} import BIP39, SLIP39, __version__", exec_globals)
    assert exec_globals["__version__"], "version is empty"

    # Test submodule imports
    exec(f"from {package}.tools import BIP39 as BIP39Tool", exec_globals)
    exec(
        f"from {package}.cli import app, deconstruct, reconstruct, version",
        exec_globals,
    )

    print(f"✓ imports: BIP39, SLIP39, __version__={exec_globals['__version__']}")


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
