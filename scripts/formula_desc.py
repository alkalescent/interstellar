#!/usr/bin/env python3
"""Print the project description, checked and escaped for the Homebrew formula.

The Update Homebrew and Smoke Homebrew steps put the description into the
formula template with sed, inside a Ruby double-quoted string. There a double
quote ends the string, #{...} runs Ruby code, and a backslash starts an escape,
so the description must not contain any of them. The sed replacement reads &
and its | delimiter, so the output escapes both.

Usage:
    python3 scripts/formula_desc.py [path/to/pyproject.toml]
"""

import sys
import tomllib
from pathlib import Path

REFUSED = {
    '"': "a double quote ends the formula's Ruby string",
    "#": "#{...} in the formula's Ruby string runs Ruby code",
    "\\": "a backslash starts an escape in the formula's Ruby string",
}


def check(description: str) -> str:
    """Return the description if the formula's Ruby string can hold it as is.

    Args:
        description: The project description from pyproject.toml.

    Returns:
        The description, unchanged.

    Raises:
        ValueError: If the description holds a refused or control character.
    """
    for char, reason in REFUSED.items():
        if char in description:
            raise ValueError(f"The description must not contain {char}: {reason}")
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in description):
        raise ValueError("The description must not contain control characters")
    return description


def sed_escape(text: str) -> str:
    """Escape & and | for a sed replacement that uses | as its delimiter."""
    return text.replace("&", r"\&").replace("|", r"\|")


def main(argv: list[str]) -> int:
    """Print the checked, escaped description, or the reason it is refused."""
    path = Path(argv[1] if len(argv) > 1 else "pyproject.toml")
    description = tomllib.loads(path.read_text(encoding="utf-8"))["project"][
        "description"
    ]
    try:
        print(sed_escape(check(description)))
    except ValueError as e:
        print(f"{path}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
