"""Tests for scripts/formula_desc.py, which feeds the Homebrew formula's desc."""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "formula_desc.py"


def run_script(pyproject: Path) -> subprocess.CompletedProcess:
    """Run the script on a pyproject.toml and return the completed process."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(pyproject)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def write_pyproject(tmp_path: Path, description: str) -> Path:
    """Write a pyproject.toml whose description parses to the given text."""
    path = tmp_path / "pyproject.toml"
    # A JSON string of ASCII text is also a valid TOML basic string
    path.write_text(
        f"[project]\ndescription = {json.dumps(description)}\n", encoding="utf-8"
    )
    return path


class TestFormulaDescription:
    """Tests for the description check and its sed escaping."""

    def test_real_description_passes(self) -> None:
        """Test the project's own description reaches the formula unchanged."""
        pyproject = ROOT / "pyproject.toml"
        description = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"][
            "description"
        ]

        result = run_script(pyproject)

        assert result.returncode == 0, result.stderr
        assert result.stdout == f"{description}\n"

    @pytest.mark.parametrize(
        "description",
        [
            'A "quoted" tool',
            "A tool #{system('id')}",
            "A tool \\ with a backslash",
        ],
        ids=["double-quote", "hash", "backslash"],
    )
    def test_ruby_string_characters_refused(
        self, tmp_path: Path, description: str
    ) -> None:
        """Test characters a Ruby double-quoted string reads are refused."""
        result = run_script(write_pyproject(tmp_path, description))

        assert result.returncode == 1
        assert result.stdout == ""
        assert "The description must not contain" in result.stderr

    def test_control_character_refused(self, tmp_path: Path) -> None:
        """Test a newline, which a TOML escape can put in the text, is refused."""
        result = run_script(write_pyproject(tmp_path, "Line one\nLine two"))

        assert result.returncode == 1
        assert "control characters" in result.stderr

    def test_sed_characters_escaped(self, tmp_path: Path) -> None:
        """Test & and the | delimiter are escaped for the sed replacement."""
        result = run_script(write_pyproject(tmp_path, "Salt & pepper | herbs"))

        assert result.returncode == 0, result.stderr
        assert result.stdout == "Salt \\& pepper \\| herbs\n"
