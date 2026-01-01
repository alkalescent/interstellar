#!/usr/bin/env python3
"""Version management utility for automatic versioning."""

import re
import sys
from datetime import datetime
from pathlib import Path


def read_version(pyproject_path: Path) -> str:
    """Read current version from pyproject.toml."""
    content = pyproject_path.read_text()
    match = re.search(
        r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def write_version(pyproject_path: Path, new_version: str) -> None:
    """Write new version to pyproject.toml."""
    content = pyproject_path.read_text()
    new_content = re.sub(
        r'^version\s*=\s*["\'][^"\']+["\']',
        f'version = "{new_version}"',
        content,
        count=1,
        flags=re.MULTILINE
    )
    pyproject_path.write_text(new_content)


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse semantic version string into (major, minor, patch)."""
    # Remove any pre-release or build metadata
    base_version = re.match(r'^(\d+)\.(\d+)\.(\d+)', version)
    if not base_version:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(map(int, base_version.groups()))


def bump_version(version: str, bump_type: str) -> str:
    """Bump version according to bump_type (major, minor, patch)."""
    major, minor, patch = parse_version(version)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def create_rc_version(version: str) -> str:
    """Create RC version with timestamp."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{version}rc{timestamp}"


def determine_bump_type(commit_messages: str, pr_labels: str) -> str:
    """Determine version bump type from commit messages or PR labels."""
    # Check PR labels first (highest priority)
    if pr_labels:
        labels = [label.strip().lower() for label in pr_labels.split(',')]
        if 'major' in labels or 'breaking' in labels:
            return 'major'
        if 'patch' in labels or 'bugfix' in labels:
            return 'patch'
        # Default to minor for PRs
        return 'minor'

    # Check commit messages
    if commit_messages:
        messages_lower = commit_messages.lower()
        if '#major' in messages_lower or 'breaking:' in messages_lower:
            return 'major'
        if '#patch' in messages_lower or 'fix:' in messages_lower:
            return 'patch'

    # Default to minor
    return 'minor'


def main():
    if len(sys.argv) < 2:
        print("Usage: version_manager.py <command> [args...]", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  read                     - Read current version", file=sys.stderr)
        print(
            "  bump <type>              - Bump version (major/minor/patch)", file=sys.stderr)
        print("  determine <commits> <labels> - Determine bump type", file=sys.stderr)
        print(
            "  rc <version>             - Create RC version with timestamp", file=sys.stderr)
        print("  update <version>         - Update pyproject.toml with version", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    if command == "read":
        version = read_version(pyproject_path)
        print(version)

    elif command == "bump":
        if len(sys.argv) < 3:
            print("Error: bump requires bump_type argument", file=sys.stderr)
            sys.exit(1)
        bump_type = sys.argv[2]
        current = read_version(pyproject_path)
        new_version = bump_version(current, bump_type)
        print(new_version)

    elif command == "determine":
        commits = sys.argv[2] if len(sys.argv) > 2 else ""
        labels = sys.argv[3] if len(sys.argv) > 3 else ""
        bump_type = determine_bump_type(commits, labels)
        print(bump_type)

    elif command == "rc":
        if len(sys.argv) < 3:
            print("Error: rc requires version argument", file=sys.stderr)
            sys.exit(1)
        version = sys.argv[2]
        rc_version = create_rc_version(version)
        print(rc_version)

    elif command == "update":
        if len(sys.argv) < 3:
            print("Error: update requires version argument", file=sys.stderr)
            sys.exit(1)
        new_version = sys.argv[2]
        write_version(pyproject_path, new_version)
        print(f"Updated version to {new_version}")

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
