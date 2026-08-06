"""Backwards-compatibility guards for previously created mnemonics and keys.

Shares produced before the slip39/hdwallet dependencies were removed must
still recover, and must still derive the same wallet. These are frozen
fixtures rather than round-trips, so a change in encoding parameters
(passphrase, iteration exponent, extendable flag, or the choice to split
BIP39 entropy rather than the seed) fails here instead of silently
orphaning someone's funds.
"""

from __future__ import annotations

import pytest
from shamir_mnemonic.share import Share

from interstellar.tools import BIP39, SLIP39

# The standard BIP39 test mnemonic and its first Ethereum address.
MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon "
    "abandon abandon abandon about"
)
ADDRESS = "0x9858EfFD232B4033E47d90003D41EC34EcaEda94"

# A frozen 2-of-3 share set for MNEMONIC, in the encoding this tool has
# always produced: the BIP39 entropy as the SLIP-39 master secret, no
# passphrase, extendable, iteration exponent 1.
GOLDEN_SHARES = (
    "luck racism academic acid champion dining dynamic pitch render plains "
    "forecast diminish extend season rocky switch mixed numerous equation greatest",
    "luck racism academic agency cards timely paper patent distance mama "
    "engage agree diet society jewelry guilt friar spew evaluate busy",
    "luck racism academic always breathe medal hearing busy knife umbrella "
    "genuine facility sunlight twin devote alive aspect spelling short smith",
)


@pytest.mark.parametrize(
    "pair", [(0, 1), (0, 2), (1, 2)], ids=["shares-1-2", "shares-1-3", "shares-2-3"]
)
def test_existing_shares_still_recover(pair: tuple[int, int]) -> None:
    """Test any two of the frozen shares rebuild the original mnemonic."""
    shares = [GOLDEN_SHARES[i] for i in pair]
    assert SLIP39().reconstruct(shares) == MNEMONIC


def test_recovered_mnemonic_derives_same_wallet() -> None:
    """Test recovery yields the same Ethereum address as before."""
    recovered = SLIP39().reconstruct(list(GOLDEN_SHARES[:2]))
    assert BIP39().eth(recovered) == ADDRESS


def test_share_encoding_parameters_unchanged() -> None:
    """Test newly created shares keep the frozen encoding parameters.

    Share values are random, so structure is compared rather than words.
    """
    old = Share.from_mnemonic(GOLDEN_SHARES[0])
    new = Share.from_mnemonic(SLIP39().deconstruct(MNEMONIC, 2, 3)[0])
    assert new.member_threshold == old.member_threshold
    assert new.group_threshold == old.group_threshold
    assert new.group_count == old.group_count
    assert new.extendable == old.extendable
    assert new.iteration_exponent == old.iteration_exponent
    assert len(GOLDEN_SHARES[0].split()) == 20


def test_single_share_is_insufficient() -> None:
    """Test the 2-of-3 threshold is enforced, not merely recorded."""
    with pytest.raises(Exception):  # noqa: B017 - library raises its own type
        SLIP39().reconstruct([GOLDEN_SHARES[0]])
