import secrets

from mnemonic import Mnemonic
from shamir_mnemonic import combine_mnemonics, generate_mnemonics
from shamir_mnemonic.share import Share
from shamir_mnemonic.wordlist import WORDLIST

from interstellar.wallet import eth_address

# SLIP-39 share length is fixed by the size of the secret it encodes.
_WORDS_TO_SECRET_BYTES = {20: 16, 33: 32}


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
        entropies = [bytes(entropy[i * size : (i + 1) * size]) for i in range(split)]
        mnemos = [self.mnemo.to_mnemonic(ent) for ent in entropies]
        # Check if the mnemonics are valid
        if not all(self.mnemo.check(m) for m in mnemos):
            raise ValueError("Invalid BIP39 mnemonics after deconstruction.")
        return mnemos

    def eth(self, mnemo: str) -> str:
        """Derive Ethereum address from BIP39 mnemonic.

        Args:
            mnemo: The BIP39 mnemonic phrase.

        Returns:
            The derived Ethereum address.
        """
        return eth_address(mnemo)

    def generate(self, num_words: int) -> str:
        """Generate a random BIP39 mnemonic.

        Args:
            num_words: Number of words (12, 15, 18, 21, or 24).

        Returns:
            A randomly generated BIP39 mnemonic phrase.

        Raises:
            ValueError: If num_words is not a supported length.
        """
        if num_words not in (12, 15, 18, 21, 24):
            raise ValueError(f"Unsupported BIP39 word count: {num_words}")
        # Each word carries 11 bits, of which one checksum bit per 32 entropy
        # bits, leaving 32/3 bits of entropy per word.
        return self.mnemo.generate(num_words * 32 // 3)


class SLIP39:
    """SLIP39 implementation for generating and reconstructing mnemonic phrases."""

    def __init__(self) -> None:
        """Initialize SLIP39 handler with wordlist and mapping."""
        self.mnemo = Mnemonic()
        self.words = WORDLIST
        assert len(self.words) == 1024 and self.words == sorted(self.words)
        self.map = {word: idx + 1 for idx, word in enumerate(self.words)}

    def deconstruct(self, mnemo: str, required: int = 2, total: int = 3) -> list[str]:
        """Deconstruct a BIP39 mnemonic into SLIP39 shares.

        The shares encode the mnemonic's BIP39 entropy as the SLIP-39 master
        secret, with no passphrase, so recovery returns the original entropy
        and therefore the original mnemonic.

        Args:
            mnemo: The BIP39 mnemonic to split.
            required: Minimum shares needed for reconstruction.
            total: Total number of shares to create.

        Returns:
            List of SLIP39 share mnemonics.

        Raises:
            ValueError: If the mnemonic is invalid.
        """
        if not self.mnemo.check(mnemo):
            raise ValueError("Invalid BIP39 mnemo.")
        entropy = bytes(self.mnemo.to_entropy(mnemo))
        groups = generate_mnemonics(1, [(required, total)], entropy)
        return list(groups[0])

    def reconstruct(self, shares: list[str]) -> str:
        """Reconstruct a BIP39 mnemonic from SLIP39 shares.

        Args:
            shares: List of SLIP39 share mnemonics.

        Returns:
            The reconstructed BIP39 mnemonic.
        """
        entropy = combine_mnemonics(shares)
        return self.mnemo.to_mnemonic(entropy)

    def get_required(self, share: str) -> int:
        """Extract required threshold from a SLIP39 share.

        Args:
            share: A single SLIP39 share mnemonic.

        Returns:
            Number of shares required for reconstruction.
        """
        share_obj = Share.from_mnemonic(share)
        return share_obj.member_threshold

    def generate(self, num_words: int) -> str:
        """Generate a random SLIP39 mnemonic.

        Args:
            num_words: Number of words (20 or 33).

        Returns:
            A randomly generated SLIP39 mnemonic phrase.

        Raises:
            ValueError: If num_words is not a supported length.
        """
        if num_words not in _WORDS_TO_SECRET_BYTES:
            raise ValueError(f"Unsupported SLIP39 word count: {num_words}")
        secret = secrets.token_bytes(_WORDS_TO_SECRET_BYTES[num_words])
        return generate_mnemonics(1, [(1, 1)], secret)[0][0]
