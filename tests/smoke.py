#!/usr/bin/env python3
"""Smoke tests for verifying installation and CLI functionality."""

import subprocess
import sys


def run(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_version(cmd: list[str]) -> None:
    """Test version command works."""
    code, out, err = run([*cmd, "version"])
    assert code == 0, f"version failed: {err}"
    version = out.strip()
    assert version, "version output empty"
    print(f"✓ version: {version}")


def test_help(cmd: list[str]) -> None:
    """Test help command works."""
    code, out, err = run([*cmd, "--help"])
    assert code == 0, f"help failed: {err}"
    assert "deconstruct" in out, "missing deconstruct command"
    assert "reconstruct" in out, "missing reconstruct command"
    print("✓ help")


def main() -> None:
    """Run smoke tests."""
    # Command can be passed as args (e.g., "./binary" or "interstellar")
    cmd = sys.argv[1:] if len(sys.argv) > 1 else ["interstellar"]

    print(f"Running smoke tests with: {' '.join(cmd)}")
    test_version(cmd)
    test_help(cmd)
    print("All smoke tests passed!")


if __name__ == "__main__":
    main()
