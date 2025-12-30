from hdwallet import HDWallet
from hdwallet.mnemonics import BIP39Mnemonic, SLIP39Mnemonic, BIP39_MNEMONIC_LANGUAGES, IMnemonic
from hdwallet.symbols import ETH
from hdwallet.cryptocurrencies import Ethereum
from mnemonic import Mnemonic
from shamir_mnemonic.wordlist import WORDLIST
import slip39


class IP39:
    def generate(self, num_words: int) -> str:
        """Generate a random mnemonic of BIP39 words."""
        mnemo = self.mnemo.generate(num_words * 32 // 3)
        return mnemo


class BIP39(IP39):
    """BIP39 class to handle mnemonic generation and validation."""

    def __init__(self):
        self.mnemo = Mnemonic()
        self.words = self.mnemo.wordlist
        assert len(self.words) == 2048 and self.words == sorted(self.words)
        self.map = {word: idx+1 for idx, word in enumerate(self.words)}

    def reconstruct(self, mnemos: list[str]) -> str:
        """Reconstruct a mnemonic from its components."""
        entropy = b''.join([self.mnemo.to_entropy(mnemo) for mnemo in mnemos])
        mnemo = self.mnemo.to_mnemonic(entropy)
        if not self.mnemo.check(mnemo):
            raise ValueError("Invalid BIP39 mnemo after reconstruction.")
        return mnemo

    def deconstruct(self, mnemo: str, split: int = 2) -> list[str]:
        """Deconstruct a mnemonic into its components."""
        # Check if the mnemo is valid
        if not self.mnemo.check(mnemo):
            raise ValueError("Invalid BIP39 mnemo.")
        # Convert the mnemo to entropy
        entropy = self.mnemo.to_entropy(mnemo)
        # Split the entropy into split parts
        size = len(entropy) // split
        entropies = [entropy[i*size:(i+1)*size] for i in range(split)]
        mnemos = [self.mnemo.to_mnemonic(ent) for ent in entropies]
        # Check if the mnemonics are valid
        if not all(self.mnemo.check(mnemo) for mnemo in mnemos):
            raise ValueError("Invalid BIP39 mnemonics after deconstruction.")
        return mnemos

    def eth(self, mnemo: str) -> str:
        mnemo = BIP39Mnemonic(mnemo)
        wallet = HDWallet(
            symbol=ETH,
            cryptocurrency=Ethereum
        ).from_mnemonic(mnemo)
        addr = wallet.address()
        return addr


class SLIP39(IP39):
    """
    SLIP39 implementation for generating and reconstructing
    mnemonic phrases.
    """

    def __init__(self):
        self.mnemo = slip39.recovery.Mnemonic()
        self.words = WORDLIST
        assert len(self.words) == 1024 and self.words == sorted(self.words)
        self.map = {word: idx+1 for idx, word in enumerate(self.words)}

    def deconstruct(self, mnemo: str, required: int = 2, total: int = 3) -> list[str]:
        """Deconstruct a mnemo into its shares."""
        _, shares = slip39.api.create(
            "LEDGER", 1, {"KEYS": (required, total)}, mnemo, using_bip39=True
        ).groups["KEYS"]
        return shares

    def reconstruct(self, shares: list[str]) -> str:
        """Reconstruct multiple shares into a mnemo."""
        entropy = slip39.recovery.recover(
            shares, using_bip39=True, as_entropy=True)
        mnemo = self.mnemo.to_mnemonic(entropy)
        return mnemo

    def get_required(self, share: str) -> int:
        """Extract required threshold from a SLIP39 share.
        Returns required number of shares needed for reconstruction."""
        from shamir_mnemonic.share import Share
        share_obj = Share.from_mnemonic(share)
        return share_obj.member_threshold

    def eth(self, mnemo: str) -> str:
        mnemo = SLIP39Mnemonic(mnemo)
        wallet = HDWallet(
            symbol=ETH,
            cryptocurrency=Ethereum
        ).from_mnemonic(mnemo)
        addr = wallet.address()
        return addr
