import slip39
from hdwallet import HDWallet
from hdwallet.cryptocurrencies import Ethereum
from hdwallet.mnemonics import (
    BIP39_MNEMONIC_LANGUAGES,
    SLIP39_MNEMONIC_LANGUAGES,
    BIP39Mnemonic,
    SLIP39Mnemonic,
)
from hdwallet.symbols import ETH
from mnemonic import Mnemonic
from shamir_mnemonic.share import Share
from shamir_mnemonic.wordlist import WORDLIST


class BIP39:
    """BIP39 class to handle mnemonic generation and validation."""

    def __init__(self) -> None:
        """Initialize BIP39 handler with wordlist and mapping."""
        self.mnemo = Mnemonic()
        self.words = self.mnemo.wordlist
        assert len(self.words) == 2048 and self.words == sorted(self.words)
        self.map = {word: idx + 1 for idx, word in enumerate(self.words)}

    def reconstruct(self, mnemos: list[str]) -> str:
        """Reconstruct a mnemonic from its components.

        Args:
            mnemos: List of partial mnemonics to combine.

        Returns:
            The reconstructed full BIP39 mnemonic.

        Raises:
            ValueError: If the reconstructed mnemonic is invalid.
        """
        entropy = b"".join([self.mnemo.to_entropy(mnemo) for mnemo in mnemos])
        mnemo = self.mnemo.to_mnemonic(entropy)
        if not self.mnemo.check(mnemo):
            raise ValueError("Invalid BIP39 mnemo after reconstruction.")
        return mnemo

    def deconstruct(self, mnemo: str, split: int = 2) -> list[str]:
        """Deconstruct a mnemonic into its components.

        Args:
            mnemo: The BIP39 mnemonic to split.
            split: Number of parts to split into (default: 2).

        Returns:
            List of partial mnemonics.

        Raises:
            ValueError: If mnemonic is invalid or cannot be evenly split.
        """
        # Check if the mnemo is valid
        if not self.mnemo.check(mnemo):
            raise ValueError("Invalid BIP39 mnemo.")
        # Convert the mnemo to entropy
        entropy = self.mnemo.to_entropy(mnemo)
        # Check if the entropy split is valid
        if len(entropy) % split:
            raise ValueError("Invalid BIP39 entropy split.")
        # Split the entropy into split parts
        size = len(entropy) // split
        entropies = [entropy[i * size : (i + 1) * size] for i in range(split)]
        mnemos = [self.mnemo.to_mnemonic(ent) for ent in entropies]
        # Check if the mnemonics are valid
        if not all(self.mnemo.check(mnemo) for mnemo in mnemos):
            raise ValueError("Invalid BIP39 mnemonics after deconstruction.")
        return mnemos

    def eth(self, mnemo: str) -> str:
        """Derive Ethereum address from BIP39 mnemonic.

        Args:
            mnemo: The BIP39 mnemonic phrase.

        Returns:
            The derived Ethereum address.
        """
        mnemo = BIP39Mnemonic(mnemo)
        wallet = HDWallet(symbol=ETH, cryptocurrency=Ethereum).from_mnemonic(mnemo)
        addr = wallet.address()
        return addr

    def generate(self, num_words: int) -> str:
        """Generate a random BIP39 mnemonic.

        Args:
            num_words: Number of words (12, 15, 18, 21, or 24).

        Returns:
            A randomly generated BIP39 mnemonic phrase.
        """
        mnemo = BIP39Mnemonic.from_words(num_words, BIP39_MNEMONIC_LANGUAGES.ENGLISH)
        return mnemo


class SLIP39:
    """
    SLIP39 implementation for generating and reconstructing
    mnemonic phrases.
    """

    def __init__(self) -> None:
        """Initialize SLIP39 handler with wordlist and mapping."""
        self.mnemo = slip39.recovery.Mnemonic()
        self.words = WORDLIST
        assert len(self.words) == 1024 and self.words == sorted(self.words)
        self.map = {word: idx + 1 for idx, word in enumerate(self.words)}

    def deconstruct(self, mnemo: str, required: int = 2, total: int = 3) -> list[str]:
        """Deconstruct a BIP39 mnemonic into SLIP39 shares.

        Args:
            mnemo: The BIP39 mnemonic to split.
            required: Minimum shares needed for reconstruction.
            total: Total number of shares to create.

        Returns:
            List of SLIP39 share mnemonics.
        """
        _, shares = slip39.api.create(
            "LEDGER", 1, {"KEYS": (required, total)}, mnemo, using_bip39=True
        ).groups["KEYS"]
        return shares

    def reconstruct(self, shares: list[str]) -> str:
        """Reconstruct a BIP39 mnemonic from SLIP39 shares.

        Args:
            shares: List of SLIP39 share mnemonics.

        Returns:
            The reconstructed BIP39 mnemonic.
        """
        entropy = slip39.recovery.recover(shares, using_bip39=True, as_entropy=True)
        mnemo = self.mnemo.to_mnemonic(entropy)
        return mnemo

    def get_required(self, share: str) -> int:
        """Extract required threshold from a SLIP39 share.

        Args:
            share: A single SLIP39 share mnemonic.

        Returns:
            Number of shares required for reconstruction.
        """
        share_obj = Share.from_mnemonic(share)
        return share_obj.member_threshold

    def eth(self, mnemo: str) -> str:
        """Derive Ethereum address from reconstructed mnemonic.

        Args:
            mnemo: The BIP39 mnemonic phrase.

        Returns:
            The derived Ethereum address.
        """
        mnemo = SLIP39Mnemonic(mnemo)
        wallet = HDWallet(symbol=ETH, cryptocurrency=Ethereum).from_mnemonic(mnemo)
        addr = wallet.address()
        return addr

    def generate(self, num_words: int) -> str:
        """Generate a random SLIP39 mnemonic.

        Args:
            num_words: Number of words for the mnemonic.

        Returns:
            A randomly generated SLIP39 mnemonic phrase.
        """
        mnemo = SLIP39Mnemonic.from_words(num_words, SLIP39_MNEMONIC_LANGUAGES.ENGLISH)
        return mnemo
