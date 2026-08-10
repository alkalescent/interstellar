"""Tests for Ethereum address derivation.

These are golden-vector tests. The addresses below are the values standard
wallets show for these seed phrases, and they are what the previous
hdwallet-backed implementation produced, so any drift in the vendored
secp256k1, BIP32, or EIP-55 code fails here.
"""

from __future__ import annotations

import pytest

from interstellar.wallet import _multiply, eth_address

# BIP39 test mnemonics paired with the first address on m/44'/60'/0'/0/0.
VECTORS = [
    (
        "abandon abandon abandon abandon abandon abandon abandon abandon "
        "abandon abandon abandon about",
        "0x9858EfFD232B4033E47d90003D41EC34EcaEda94",
    ),
    (
        "legal winner thank year wave sausage worth useful legal winner thank yellow",
        "0x58A57ed9d8d624cBD12e2C467D34787555bB1b25",
    ),
    (
        "zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong",
        "0xfc2077CA7F403cBECA41B1B0F62D91B5EA631B5E",
    ),
]

# secp256k1 generator, from SEC 2.
GENERATOR = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)
# 2G, a published multiple used to check the point arithmetic directly.
DOUBLE_GENERATOR = (
    0xC6047F9441ED7D6D3045406E95C07CD85C778E4B8CEF3CA7ABAC09B95C709EE5,
    0x1AE168FEA63DC339A3C58419466CEAEEF7F632653266D0E1236431A950CFE52A,
)


@pytest.mark.parametrize(("mnemonic", "expected"), VECTORS)
def test_known_addresses(mnemonic: str, expected: str) -> None:
    """Test derivation reproduces the standard BIP44 addresses."""
    assert eth_address(mnemonic) == expected


def test_scalar_multiplication_vectors() -> None:
    """Test point arithmetic against published multiples of the generator."""
    assert _multiply(1) == GENERATOR
    assert _multiply(2) == DOUBLE_GENERATOR


def test_checksum_is_eip55_not_lowercase() -> None:
    """Test the address carries EIP-55 mixed-case, not a plain hex string."""
    address = eth_address(VECTORS[0][0])
    assert address.startswith("0x")
    assert len(address) == 42
    assert address != address.lower()


def test_passphrase_changes_address() -> None:
    """Test a BIP39 passphrase derives a different wallet."""
    mnemonic = VECTORS[0][0]
    assert eth_address(mnemonic, "trezor") != eth_address(mnemonic)


def test_derivation_is_deterministic() -> None:
    """Test repeated derivation returns the same address."""
    mnemonic = VECTORS[0][0]
    assert eth_address(mnemonic) == eth_address(mnemonic)
