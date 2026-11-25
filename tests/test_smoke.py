"""Tests for the EXPECTED_VERSION check in tests/smoke.py."""

import sys

import pytest
import smoke

# Stands in for the CLI: prints v1.2.3 whatever arguments follow
FAKE_CLI = [sys.executable, "-c", "print('v1.2.3')"]


class TestSmokeVersion:
    """Tests for smoke.test_version against EXPECTED_VERSION."""

    def test_unset_expected_version_passes(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test a local run without EXPECTED_VERSION checks only the format."""
        monkeypatch.delenv("EXPECTED_VERSION", raising=False)
        smoke.test_version(FAKE_CLI)

    def test_matching_version_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test the version passes when it equals EXPECTED_VERSION."""
        monkeypatch.setenv("EXPECTED_VERSION", "v1.2.3")
        smoke.test_version(FAKE_CLI)

    def test_other_version_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test the version fails when it differs from EXPECTED_VERSION."""
        monkeypatch.setenv("EXPECTED_VERSION", "v9.9.9")
        with pytest.raises(AssertionError, match="!= expected v9.9.9"):
            smoke.test_version(FAKE_CLI)

    def test_empty_expected_version_fails(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test a set but empty EXPECTED_VERSION fails, since CI lost the value."""
        monkeypatch.setenv("EXPECTED_VERSION", "")
        with pytest.raises(AssertionError, match="set but empty"):
            smoke.test_version(FAKE_CLI)
