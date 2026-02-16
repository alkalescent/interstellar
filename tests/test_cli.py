import json
import os
import tempfile
from typing import Any

from conftest import SPLIT_PARTS, WORDS_24, assert_eth_addr
from packaging.version import parse as parse_version
from typer.testing import CliRunner

from interstellar.cli import app
from interstellar.tools import BIP39, SLIP39

runner = CliRunner()


def assert_success_with_json(result: Any) -> dict[str, Any]:
    """Assert command succeeded and return parsed JSON output."""
    assert result.exit_code == 0
    return json.loads(result.stdout)


class TestVersion:
    """Test the version CLI command."""

    def test_version(self) -> None:
        """Test version command returns a valid version string."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        version_str = result.stdout.strip()
        assert version_str  # Not empty
        assert version_str.startswith("v"), "Version should start with 'v'"
        # Strip 'v' prefix and validate it's a proper PEP 440 version string
        parsed = parse_version(version_str.removeprefix("v"))
        assert parsed.release, "Version must have at least one release segment"


class TestDeconstruct:
    """Test the deconstruct CLI command."""

    def setup_method(self) -> None:
        """Setup test fixtures."""
        self.bip39 = BIP39()
        self.mnemo_24 = self.bip39.generate(WORDS_24)

    def test_bip39_option(self) -> None:
        """Test BIP39 deconstruction from --mnemonic option."""
        result = runner.invoke(
            app, ["deconstruct", "--mnemonic", self.mnemo_24, "--standard", "BIP39"]
        )

        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert isinstance(output, list)
        assert len(output) == SPLIT_PARTS
        assert all(item["standard"] == "BIP39" for item in output)
        assert all("mnemonic" in item for item in output)
        for item in output:
            assert_eth_addr(item.get("eth_addr"))

    def test_slip39_default(self) -> None:
        """Test SLIP39 deconstruction with default 2-of-3."""
        result = runner.invoke(app, ["deconstruct", "--mnemonic", self.mnemo_24])

        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["standard"] == "SLIP39"
        assert len(output["shares"]) == SPLIT_PARTS
        assert all(len(group) == 3 for group in output["shares"])

    def test_slip39_3of5(self) -> None:
        """Test SLIP39 deconstruction with custom 3-of-5."""
        result = runner.invoke(
            app,
            [
                "deconstruct",
                "--mnemonic",
                self.mnemo_24,
                "--required",
                "3",
                "--total",
                "5",
            ],
        )

        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["standard"] == "SLIP39"
        assert len(output["shares"]) == SPLIT_PARTS
        assert all(len(group) == 5 for group in output["shares"])

    def test_slip39_5of7(self) -> None:
        """Test SLIP39 deconstruction with custom 5-of-7."""
        result = runner.invoke(
            app,
            [
                "deconstruct",
                "--mnemonic",
                self.mnemo_24,
                "--required",
                "5",
                "--total",
                "7",
            ],
        )

        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["standard"] == "SLIP39"
        assert len(output["shares"]) == SPLIT_PARTS
        assert all(len(group) == 7 for group in output["shares"])

    def test_from_file(self) -> None:
        """Test deconstruction from file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(self.mnemo_24)
            temp_file = f.name

        try:
            result = runner.invoke(
                app, ["deconstruct", "--filename", temp_file, "--standard", "BIP39"]
            )

            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert len(output) == SPLIT_PARTS
        finally:
            os.unlink(temp_file)

    def test_with_digits(self) -> None:
        """Test deconstruction with digits output."""
        result = runner.invoke(
            app, ["deconstruct", "--mnemonic", self.mnemo_24, "--digits"]
        )

        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["digits"] is True
        # Verify shares contain digits
        first_share = output["shares"][0][0]
        assert all(word.isdigit() or word == " " for word in first_share)

    def test_invalid_standard(self) -> None:
        """Test deconstruction with invalid standard."""
        result = runner.invoke(
            app, ["deconstruct", "--mnemonic", self.mnemo_24, "--standard", "INVALID"]
        )

        assert result.exit_code != 0
        # Error is raised as exception, check the exception
        assert result.exception is not None

    def test_missing_mnemonic(self) -> None:
        """Test deconstruction without mnemonic or file."""
        result = runner.invoke(app, ["deconstruct"])

        assert result.exit_code != 0


class TestReconstruct:
    """Test the reconstruct CLI command."""

    def setup_method(self) -> None:
        """Setup test fixtures."""
        self.bip39 = BIP39()
        self.slip39 = SLIP39()
        self.mnemo_24 = self.bip39.generate(WORDS_24)

    def test_slip39_file(self) -> None:
        """Test SLIP39 reconstruction from file."""
        # Create shares
        bip_parts = self.bip39.deconstruct(self.mnemo_24, SPLIT_PARTS)
        shares_group1 = self.slip39.deconstruct(bip_parts[0], required=2, total=3)
        shares_group2 = self.slip39.deconstruct(bip_parts[1], required=2, total=3)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(f"{shares_group1[0]},{shares_group1[1]}\n")
            f.write(f"{shares_group2[0]},{shares_group2[1]}\n")
            temp_file = f.name

        try:
            result = runner.invoke(app, ["reconstruct", "--filename", temp_file])

            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert output["standard"] == "BIP39"
            assert output["mnemonic"] == self.mnemo_24
            assert output["required"] == 2
            assert_eth_addr(output.get("eth_addr"))
            # Note: total cannot be reliably inferred from shares (not encoded in SLIP39)
            # It returns group_count which is 1 in our scheme
        finally:
            os.unlink(temp_file)

    def test_slip39_option(self) -> None:
        """Test SLIP39 reconstruction from --shares option."""
        bip_parts = self.bip39.deconstruct(self.mnemo_24, SPLIT_PARTS)
        shares_group1 = self.slip39.deconstruct(bip_parts[0], required=2, total=3)
        shares_group2 = self.slip39.deconstruct(bip_parts[1], required=2, total=3)

        shares_str = f"{shares_group1[0]},{shares_group1[1]};{shares_group2[0]},{shares_group2[1]}"

        result = runner.invoke(app, ["reconstruct", "--shares", shares_str])

        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["standard"] == "BIP39"
        assert output["mnemonic"] == self.mnemo_24
        assert_eth_addr(output.get("eth_addr"))

    def test_bip39_file(self) -> None:
        """Test BIP39 reconstruction from file."""
        # Use CLI to get properly formatted BIP39 output
        result = runner.invoke(
            app, ["deconstruct", "--mnemonic", self.mnemo_24, "--standard", "BIP39"]
        )
        decon_output = json.loads(result.stdout)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            # Write as comma-separated values for each group (one BIP39 part per group)
            f.write(f"{decon_output[0]['mnemonic']}\n")
            f.write(f"{decon_output[1]['mnemonic']}\n")
            temp_file = f.name

        try:
            result = runner.invoke(
                app, ["reconstruct", "--filename", temp_file, "--standard", "BIP39"]
            )

            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert output["standard"] == "BIP39"
            assert output["mnemonic"] == self.mnemo_24
        finally:
            os.unlink(temp_file)

    def test_with_digits(self) -> None:
        """Test reconstruction with digits input."""
        bip_parts = self.bip39.deconstruct(self.mnemo_24, SPLIT_PARTS)
        shares_group1 = self.slip39.deconstruct(bip_parts[0], required=2, total=3)
        shares_group2 = self.slip39.deconstruct(bip_parts[1], required=2, total=3)

        # Convert to digits
        digit_shares_g1 = [
            " ".join(str(self.slip39.map[word]) for word in share.split())
            for share in shares_group1[:2]
        ]
        digit_shares_g2 = [
            " ".join(str(self.slip39.map[word]) for word in share.split())
            for share in shares_group2[:2]
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(f"{digit_shares_g1[0]},{digit_shares_g1[1]}\n")
            f.write(f"{digit_shares_g2[0]},{digit_shares_g2[1]}\n")
            temp_file = f.name

        try:
            result = runner.invoke(
                app, ["reconstruct", "--filename", temp_file, "--digits"]
            )

            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert output["mnemonic"] == self.mnemo_24
            assert output["digits"] is True
            assert_eth_addr(output.get("eth_addr"))
        finally:
            os.unlink(temp_file)

    def test_invalid_standard(self) -> None:
        """Test reconstruction with invalid standard."""
        result = runner.invoke(
            app, ["reconstruct", "--shares", "dummy", "--standard", "INVALID"]
        )

        assert result.exit_code != 0
        # Error is raised as exception
        assert result.exception is not None

    def test_missing_shares(self) -> None:
        """Test reconstruction without shares or file."""
        result = runner.invoke(app, ["reconstruct"])

        assert result.exit_code != 0

    def test_slip39_digits_zero_index(self) -> None:
        """Test reconstruction fails with zero index for SLIP39."""
        # Create fake shares with index 0 (invalid for 1-indexed wordlist)
        invalid_shares = "0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20,1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"

        result = runner.invoke(
            app, ["reconstruct", "--shares", invalid_shares, "--digits"]
        )

        assert result.exit_code != 0
        assert "Invalid SLIP39 word index: 0" in str(
            result.output
        ) or "Invalid SLIP39 word index: 0" in str(result.exception)

    def test_slip39_digits_out_of_bounds(self) -> None:
        """Test reconstruction fails with out-of-bounds index for SLIP39."""
        # SLIP39 wordlist is 1-1024, so 1025 is out of bounds
        invalid_shares = "1025 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20,1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"

        result = runner.invoke(
            app, ["reconstruct", "--shares", invalid_shares, "--digits"]
        )

        assert result.exit_code != 0
        assert "Invalid SLIP39 word index: 1025" in str(
            result.output
        ) or "Invalid SLIP39 word index: 1025" in str(result.exception)

    def test_bip39_digits_zero_index(self) -> None:
        """Test reconstruction fails with zero index for BIP39."""
        # Create fake BIP39 parts with index 0 (invalid)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("0 1 2 3 4 5 6 7 8 9 10 11\n")
            f.write("1 2 3 4 5 6 7 8 9 10 11 12\n")
            temp_file = f.name

        try:
            result = runner.invoke(
                app,
                [
                    "reconstruct",
                    "--filename",
                    temp_file,
                    "--standard",
                    "BIP39",
                    "--digits",
                ],
            )

            assert result.exit_code != 0
            assert "Invalid BIP39 word index: 0" in str(
                result.output
            ) or "Invalid BIP39 word index: 0" in str(result.exception)
        finally:
            os.unlink(temp_file)

    def test_bip39_digits_out_of_bounds(self) -> None:
        """Test reconstruction fails with out-of-bounds index for BIP39."""
        # BIP39 wordlist is 1-2048, so 2049 is out of bounds
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("2049 1 2 3 4 5 6 7 8 9 10 11\n")
            f.write("1 2 3 4 5 6 7 8 9 10 11 12\n")
            temp_file = f.name

        try:
            result = runner.invoke(
                app,
                [
                    "reconstruct",
                    "--filename",
                    temp_file,
                    "--standard",
                    "BIP39",
                    "--digits",
                ],
            )

            assert result.exit_code != 0
            assert "Invalid BIP39 word index: 2049" in str(
                result.output
            ) or "Invalid BIP39 word index: 2049" in str(result.exception)
        finally:
            os.unlink(temp_file)

    def test_slip39_digits_invalid_non_integer(self) -> None:
        """Test reconstruction fails with non-integer string for SLIP39."""
        invalid_shares = "1 2 3 abc 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20,1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"

        result = runner.invoke(
            app, ["reconstruct", "--shares", invalid_shares, "--digits"]
        )

        assert result.exit_code != 0
        assert "Invalid SLIP39 digit: 'abc'" in str(
            result.output
        ) or "Invalid SLIP39 digit: 'abc'" in str(result.exception)

    def test_bip39_digits_invalid_non_integer(self) -> None:
        """Test reconstruction fails with non-integer string for BIP39."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("1 2 3 xyz 5 6 7 8 9 10 11 12\n")
            f.write("1 2 3 4 5 6 7 8 9 10 11 12\n")
            temp_file = f.name

        try:
            result = runner.invoke(
                app,
                [
                    "reconstruct",
                    "--filename",
                    temp_file,
                    "--standard",
                    "BIP39",
                    "--digits",
                ],
            )

            assert result.exit_code != 0
            assert "Invalid BIP39 digit: 'xyz'" in str(
                result.output
            ) or "Invalid BIP39 digit: 'xyz'" in str(result.exception)
        finally:
            os.unlink(temp_file)


class TestRoundtrip:
    """Test full roundtrip: deconstruct -> reconstruct."""

    def setup_method(self) -> None:
        """Setup test fixtures."""
        self.bip39 = BIP39()
        self.mnemo_24 = self.bip39.generate(WORDS_24)

    def test_default_2of3(self) -> None:
        """Test full roundtrip with default 2-of-3 threshold."""
        # Deconstruct
        result = runner.invoke(app, ["deconstruct", "--mnemonic", self.mnemo_24])

        assert result.exit_code == 0
        decon_output = json.loads(result.stdout)

        # Extract 2 shares from each group
        shares_str = f"{decon_output['shares'][0][0]},{decon_output['shares'][0][1]};"
        shares_str += f"{decon_output['shares'][1][0]},{decon_output['shares'][1][1]}"

        # Reconstruct
        result = runner.invoke(app, ["reconstruct", "--shares", shares_str])

        assert result.exit_code == 0
        recon_output = json.loads(result.stdout)

        # Verify roundtrip
        assert recon_output["mnemonic"] == self.mnemo_24
        assert recon_output["required"] == 2
        assert_eth_addr(recon_output.get("eth_addr"))
        # Note: total cannot be reliably inferred from shares

    def test_3of5(self) -> None:
        """Test full roundtrip with 3-of-5 threshold."""
        # Deconstruct
        result = runner.invoke(
            app,
            [
                "deconstruct",
                "--mnemonic",
                self.mnemo_24,
                "--required",
                "3",
                "--total",
                "5",
            ],
        )

        assert result.exit_code == 0
        decon_output = json.loads(result.stdout)

        # Extract 3 shares from each group
        shares_str = f"{decon_output['shares'][0][0]},{decon_output['shares'][0][1]},{decon_output['shares'][0][2]};"
        shares_str += f"{decon_output['shares'][1][0]},{decon_output['shares'][1][1]},{decon_output['shares'][1][2]}"

        # Reconstruct
        result = runner.invoke(app, ["reconstruct", "--shares", shares_str])

        assert result.exit_code == 0
        recon_output = json.loads(result.stdout)

        # Verify roundtrip and auto-detected thresholds
        assert recon_output["mnemonic"] == self.mnemo_24
        assert recon_output["required"] == 3
        assert_eth_addr(recon_output.get("eth_addr"))
        # Note: total cannot be reliably inferred from shares

    def test_5of7(self) -> None:
        """Test full roundtrip with 5-of-7 threshold."""
        # Deconstruct
        result = runner.invoke(
            app,
            [
                "deconstruct",
                "--mnemonic",
                self.mnemo_24,
                "--required",
                "5",
                "--total",
                "7",
            ],
        )

        assert result.exit_code == 0
        decon_output = json.loads(result.stdout)

        # Extract 5 shares from each group
        shares_str = (
            ",".join(decon_output["shares"][0][:5])
            + ";"
            + ",".join(decon_output["shares"][1][:5])
        )

        # Reconstruct
        result = runner.invoke(app, ["reconstruct", "--shares", shares_str])

        assert result.exit_code == 0
        recon_output = json.loads(result.stdout)

        # Verify roundtrip and auto-detected thresholds
        assert recon_output["mnemonic"] == self.mnemo_24
        assert recon_output["required"] == 5
        assert_eth_addr(recon_output.get("eth_addr"))
        # Note: total cannot be reliably inferred from shares

    def test_bip39_only(self) -> None:
        """Test BIP39-only roundtrip (no SLIP39)."""
        # Deconstruct to BIP39
        result = runner.invoke(
            app, ["deconstruct", "--mnemonic", self.mnemo_24, "--standard", "BIP39"]
        )

        assert result.exit_code == 0
        decon_output = json.loads(result.stdout)
        assert isinstance(decon_output, list)
        assert len(decon_output) == 2

        # Create file with BIP39 parts (one per line for get_mnemos)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(f"{decon_output[0]['mnemonic']}\n")
            f.write(f"{decon_output[1]['mnemonic']}\n")
            temp_file = f.name

        try:
            # Reconstruct from BIP39
            result = runner.invoke(
                app, ["reconstruct", "--filename", temp_file, "--standard", "BIP39"]
            )

            assert result.exit_code == 0
            recon_output = json.loads(result.stdout)

            # Verify roundtrip
            assert recon_output["mnemonic"] == self.mnemo_24
        finally:
            os.unlink(temp_file)

    def test_bip39_with_digits(self) -> None:
        """Test BIP39-only roundtrip with digits mode."""
        # Deconstruct to BIP39 with digits
        result = runner.invoke(
            app,
            [
                "deconstruct",
                "--mnemonic",
                self.mnemo_24,
                "--standard",
                "BIP39",
                "--digits",
            ],
        )

        assert result.exit_code == 0
        decon_output = json.loads(result.stdout)
        assert isinstance(decon_output, list)
        assert len(decon_output) == 2
        assert decon_output[0]["digits"] is True
        assert decon_output[1]["digits"] is True
        # Verify mnemonics are in digit format (space-separated numbers)
        first_mnemonic = decon_output[0]["mnemonic"]
        assert all(char.isdigit() or char == " " for char in first_mnemonic)

        # Create file with BIP39 digit parts (one per line)
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(f"{decon_output[0]['mnemonic']}\n")
            f.write(f"{decon_output[1]['mnemonic']}\n")
            temp_file = f.name

        try:
            # Reconstruct from BIP39 digits
            result = runner.invoke(
                app,
                [
                    "reconstruct",
                    "--filename",
                    temp_file,
                    "--standard",
                    "BIP39",
                    "--digits",
                ],
            )

            assert result.exit_code == 0
            recon_output = json.loads(result.stdout)

            # Verify roundtrip
            assert recon_output["mnemonic"] == self.mnemo_24
            assert recon_output["digits"] is True
        finally:
            os.unlink(temp_file)

    def test_with_digits(self) -> None:
        """Test full roundtrip with digits mode."""
        # Deconstruct with digits
        result = runner.invoke(
            app, ["deconstruct", "--mnemonic", self.mnemo_24, "--digits"]
        )

        assert result.exit_code == 0
        decon_output = json.loads(result.stdout)
        assert decon_output["digits"] is True

        # Create file with digit shares
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(f"{decon_output['shares'][0][0]},{decon_output['shares'][0][1]}\n")
            f.write(f"{decon_output['shares'][1][0]},{decon_output['shares'][1][1]}\n")
            temp_file = f.name

        try:
            # Reconstruct with digits
            result = runner.invoke(
                app, ["reconstruct", "--filename", temp_file, "--digits"]
            )

            assert result.exit_code == 0
            recon_output = json.loads(result.stdout)

            # Verify roundtrip
            assert recon_output["mnemonic"] == self.mnemo_24
            assert recon_output["digits"] is True
            assert_eth_addr(recon_output.get("eth_addr"))
        finally:
            os.unlink(temp_file)

    def test_file_based(self) -> None:
        """Test full roundtrip using files for both operations."""
        # Write mnemonic to file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(self.mnemo_24)
            input_file = f.name

        try:
            # Deconstruct from file
            result = runner.invoke(app, ["deconstruct", "--filename", input_file])

            assert result.exit_code == 0
            decon_output = json.loads(result.stdout)

            # Write shares to file
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".txt"
            ) as f:
                f.write(
                    f"{decon_output['shares'][0][0]},{decon_output['shares'][0][1]}\n"
                )
                f.write(
                    f"{decon_output['shares'][1][0]},{decon_output['shares'][1][1]}\n"
                )
                shares_file = f.name

            try:
                # Reconstruct from file
                result = runner.invoke(app, ["reconstruct", "--filename", shares_file])

                assert result.exit_code == 0
                recon_output = json.loads(result.stdout)

                # Verify roundtrip
                assert recon_output["mnemonic"] == self.mnemo_24
                assert_eth_addr(recon_output.get("eth_addr"))
            finally:
                os.unlink(shares_file)
        finally:
            os.unlink(input_file)


class TestAutoDetect:
    """Test automatic required/total detection from shares."""

    def setup_method(self) -> None:
        """Setup test fixtures."""
        self.bip39 = BIP39()
        self.slip39 = SLIP39()
        self.mnemo_24 = self.bip39.generate(WORDS_24)

    def test_2of3(self) -> None:
        """Test auto-detection of 2-of-3 threshold."""
        bip_parts = self.bip39.deconstruct(self.mnemo_24, SPLIT_PARTS)
        shares_group1 = self.slip39.deconstruct(bip_parts[0], required=2, total=3)
        shares_group2 = self.slip39.deconstruct(bip_parts[1], required=2, total=3)

        shares_str = f"{shares_group1[0]},{shares_group1[1]};{shares_group2[0]},{shares_group2[1]}"

        result = runner.invoke(app, ["reconstruct", "--shares", shares_str])

        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["required"] == 2
        assert_eth_addr(output.get("eth_addr"))
        # Note: total cannot be reliably inferred from shares

    def test_3of5(self) -> None:
        """Test auto-detection of 3-of-5 threshold."""
        bip_parts = self.bip39.deconstruct(self.mnemo_24, SPLIT_PARTS)
        shares_group1 = self.slip39.deconstruct(bip_parts[0], required=3, total=5)
        shares_group2 = self.slip39.deconstruct(bip_parts[1], required=3, total=5)

        shares_str = f"{shares_group1[0]},{shares_group1[1]},{shares_group1[2]};"
        shares_str += f"{shares_group2[0]},{shares_group2[1]},{shares_group2[2]}"

        result = runner.invoke(app, ["reconstruct", "--shares", shares_str])

        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["required"] == 3
        assert_eth_addr(output.get("eth_addr"))
        # Note: total cannot be reliably inferred from shares

    def test_5of7(self) -> None:
        """Test auto-detection of 5-of-7 threshold."""
        bip_parts = self.bip39.deconstruct(self.mnemo_24, SPLIT_PARTS)
        shares_group1 = self.slip39.deconstruct(bip_parts[0], required=5, total=7)
        shares_group2 = self.slip39.deconstruct(bip_parts[1], required=5, total=7)

        shares_str = ",".join(shares_group1[:5]) + ";" + ",".join(shares_group2[:5])

        result = runner.invoke(app, ["reconstruct", "--shares", shares_str])

        assert result.exit_code == 0
        output = json.loads(result.stdout)
        assert output["required"] == 5
        assert_eth_addr(output.get("eth_addr"))
        # Note: total cannot be reliably inferred from shares

    def test_with_digits(self) -> None:
        """Test auto-detection works with digits mode."""
        bip_parts = self.bip39.deconstruct(self.mnemo_24, SPLIT_PARTS)
        shares_group1 = self.slip39.deconstruct(bip_parts[0], required=3, total=5)
        shares_group2 = self.slip39.deconstruct(bip_parts[1], required=3, total=5)

        # Convert to digits
        digit_shares_g1 = [
            " ".join(str(self.slip39.map[word]) for word in share.split())
            for share in shares_group1[:3]
        ]
        digit_shares_g2 = [
            " ".join(str(self.slip39.map[word]) for word in share.split())
            for share in shares_group2[:3]
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write(",".join(digit_shares_g1) + "\n")
            f.write(",".join(digit_shares_g2) + "\n")
            temp_file = f.name

        try:
            result = runner.invoke(
                app, ["reconstruct", "--filename", temp_file, "--digits"]
            )

            assert result.exit_code == 0
            output = json.loads(result.stdout)
            assert output["required"] == 3
            assert_eth_addr(output.get("eth_addr"))
            # Note: total cannot be reliably inferred from shares
        finally:
            os.unlink(temp_file)
