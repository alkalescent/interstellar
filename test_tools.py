import pytest
from tools import BIP39, SLIP39
from conftest import WORDS_24, SPLIT_PARTS, assert_eth_addr

# Test constants
WORDS_12 = 12
BIP39_WORDLIST_SIZE = 2048
SLIP39_WORDLIST_SIZE = 1024
SHARES_REQUIRED = 2
SHARES_TOTAL = 3
TEST_ITERATIONS = 5


class TestBIP39:
    """Test BIP39 mnemonic generation and validation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.bip39 = BIP39()

    def test_gen_12_words(self):
        """Test generating a 12-word mnemonic."""
        mnemo = self.bip39.generate(WORDS_12)
        words = mnemo.split()
        assert len(words) == WORDS_12
        assert self.bip39.mnemo.check(mnemo)

    def test_gen_24_words(self):
        """Test generating a 24-word mnemonic."""
        mnemo = self.bip39.generate(WORDS_24)
        words = mnemo.split()
        assert len(words) == WORDS_24
        assert self.bip39.mnemo.check(mnemo)

    def test_24_word_roundtrip(self):
        """Test deconstructing and reconstructing a 24-word mnemonic."""
        mnemo = self.bip39.generate(WORDS_24)
        parts = self.bip39.deconstruct(mnemo, split=SPLIT_PARTS)

        assert len(parts) == SPLIT_PARTS
        assert all(self.bip39.mnemo.check(part) for part in parts)

        reconstructed = self.bip39.reconstruct(parts)
        assert reconstructed == mnemo

    def test_entropy_validation(self):
        """Test that 12-word mnemonic cannot be split into 2 parts (8-byte entropy is invalid)."""
        mnemo = self.bip39.generate(WORDS_12)
        # 12-word mnemonic has 16 bytes of entropy, splitting gives 8 bytes each
        # which is not a valid BIP39 entropy size (must be 16, 20, 24, 28, or 32)
        with pytest.raises(ValueError):
            self.bip39.deconstruct(mnemo, split=SPLIT_PARTS)

    def test_invalid_mnemo(self):
        """Test that invalid mnemonic raises error on deconstruct."""
        invalid_mnemo = "invalid mnemonic phrase here test fail bad"
        with pytest.raises(ValueError, match="Invalid BIP39 mnemo"):
            self.bip39.deconstruct(invalid_mnemo)

    def test_wordlist(self):
        """Test BIP39 wordlist has correct properties."""
        assert len(self.bip39.words) == BIP39_WORDLIST_SIZE
        assert self.bip39.words == sorted(self.bip39.words)
        assert len(self.bip39.map) == BIP39_WORDLIST_SIZE

    def test_consistency(self):
        """Test that generate produces valid mnemonics consistently."""
        for _ in range(TEST_ITERATIONS):
            mnemo = self.bip39.generate(WORDS_24)
            assert self.bip39.mnemo.check(mnemo)
            assert len(mnemo.split()) == WORDS_24

    def test_eth(self):
        """Test Ethereum address derivation from mnemonic."""
        mnemo = self.bip39.generate(WORDS_12)
        address = self.bip39.eth(mnemo)
        assert_eth_addr(address)


class TestSLIP39:
    """Test SLIP39 mnemonic generation and validation."""

    def setup_method(self):
        """Setup test fixtures."""
        self.slip39 = SLIP39()

    def test_gen_24_words(self):
        """Test generating a 24-word mnemonic."""
        mnemo = self.slip39.generate(WORDS_24)
        words = mnemo.split()
        assert len(words) == WORDS_24

    def test_24_word_roundtrip(self):
        """Test deconstructing and reconstructing a 24-word mnemonic."""
        mnemo = self.slip39.generate(WORDS_24)
        shares = self.slip39.deconstruct(
            mnemo, required=SHARES_REQUIRED, total=SHARES_TOTAL)

        assert len(shares) == SHARES_TOTAL

        # Should be able to reconstruct with any 2 shares
        reconstructed = self.slip39.reconstruct(shares[:SHARES_REQUIRED])
        assert reconstructed == mnemo

    def test_share_combos(self):
        """Test reconstruction with different share combinations."""
        mnemo = self.slip39.generate(WORDS_24)
        shares = self.slip39.deconstruct(
            mnemo, required=SHARES_REQUIRED, total=SHARES_TOTAL)

        # Test all possible 2-share combinations
        assert self.slip39.reconstruct(shares[:SHARES_REQUIRED]) == mnemo
        assert self.slip39.reconstruct(shares[1:]) == mnemo
        assert self.slip39.reconstruct(
            [shares[0], shares[SHARES_REQUIRED]]) == mnemo

    def test_wordlist(self):
        """Test SLIP39 wordlist has correct properties."""
        assert len(self.slip39.words) == SLIP39_WORDLIST_SIZE
        assert self.slip39.words == sorted(self.slip39.words)
        assert len(self.slip39.map) == SLIP39_WORDLIST_SIZE


class TestIntegration:
    """Integration tests for the complete workflow."""

    def setup_method(self):
        """Setup test fixtures."""
        self.bip39 = BIP39()
        self.slip39 = SLIP39()

    def test_full_24_word_workflow(self):
        """Test the complete workflow from main function with 24-word mnemonic."""
        # Generate initial mnemonic
        mnemo = self.bip39.generate(WORDS_24)

        # Deconstruct into 2 BIP39 parts
        bip_one, bip_two = self.bip39.deconstruct(mnemo, split=SPLIT_PARTS)
        assert self.bip39.mnemo.check(bip_one)
        assert self.bip39.mnemo.check(bip_two)

        # Convert first BIP39 part to SLIP39 shares
        slip_one = self.slip39.deconstruct(
            bip_one, required=SHARES_REQUIRED, total=SHARES_TOTAL)
        assert len(slip_one) == SHARES_TOTAL

        # Reconstruct first BIP39 part
        bip_one_reconstructed = self.slip39.reconstruct(
            slip_one[:SHARES_REQUIRED])
        assert bip_one_reconstructed == bip_one

        # Convert second BIP39 part to SLIP39 shares
        slip_two = self.slip39.deconstruct(
            bip_two, required=SHARES_REQUIRED, total=SHARES_TOTAL)
        assert len(slip_two) == SHARES_TOTAL

        # Reconstruct second BIP39 part
        bip_two_reconstructed = self.slip39.reconstruct(
            slip_two[:SHARES_REQUIRED])
        assert bip_two_reconstructed == bip_two

        # Reconstruct full mnemonic
        mnemo_reconstructed = self.bip39.reconstruct(
            [bip_one_reconstructed, bip_two_reconstructed])
        assert mnemo_reconstructed == mnemo

    def test_12_word_direct(self):
        """Test SLIP39 workflow with 12-word mnemonic (no BIP39 splitting)."""
        # Generate initial mnemonic
        mnemo = self.bip39.generate(WORDS_12)

        # Cannot deconstruct 12-word BIP39 into 2 parts (entropy too small)
        # Instead, test SLIP39 directly on the 12-word mnemonic
        shares = self.slip39.deconstruct(
            mnemo, required=SHARES_REQUIRED, total=SHARES_TOTAL)

        # Reconstruct from shares
        mnemo_reconstructed = self.slip39.reconstruct(shares[:SHARES_REQUIRED])
        assert mnemo_reconstructed == mnemo

    def test_bip39_iterations(self):
        """Test multiple iterations to ensure consistency."""
        for _ in range(TEST_ITERATIONS):
            mnemo = self.bip39.generate(WORDS_24)
            parts = self.bip39.deconstruct(mnemo, split=SPLIT_PARTS)
            reconstructed = self.bip39.reconstruct(parts)
            assert reconstructed == mnemo

    def test_slip39_iterations(self):
        """Test SLIP39 multiple iterations to ensure consistency."""
        for _ in range(TEST_ITERATIONS):
            mnemo = self.slip39.generate(WORDS_24)
            shares = self.slip39.deconstruct(
                mnemo, required=SHARES_REQUIRED, total=SHARES_TOTAL)
            reconstructed = self.slip39.reconstruct(shares[:SHARES_REQUIRED])
            assert reconstructed == mnemo
