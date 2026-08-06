"""Ethereum address derivation from a BIP39 mnemonic.

Implements the standard path in pure Python so the package has no compiled
dependency:

* secp256k1 point arithmetic (SEC 2 domain parameters)
* BIP32 hierarchical key derivation
* BIP44 account path ``m/44'/60'/0'/0/0``
* EIP-55 checksummed address encoding

Scalar multiplication is a straightforward double-and-add and is therefore
not constant time. This tool derives an address from a mnemonic the caller
already holds, on their own machine, and the CLI accepts that mnemonic as a
command-line argument, so timing is not the narrowest part of the threat
model. Do not reuse this module for signing in a hostile setting.
"""

from __future__ import annotations

import hmac
from hashlib import sha512

from mnemonic import Mnemonic

from interstellar.keccak import keccak256

# secp256k1 domain parameters (SEC 2, section 2.4.1).
_P = 2**256 - 2**32 - 977
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
_GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
_G = (_GX, _GY)

_HARDENED = 1 << 31

# BIP44 path for the first Ethereum account: m/44'/60'/0'/0/0
_ETH_PATH: tuple[int, ...] = (44 + _HARDENED, 60 + _HARDENED, 0 + _HARDENED, 0, 0)

Point = tuple[int, int]


def _add(p: Point | None, q: Point | None) -> Point | None:
    """Add two points on secp256k1.

    Args:
        p: First point, or None for the point at infinity.
        q: Second point, or None for the point at infinity.

    Returns:
        The sum, or None for the point at infinity.
    """
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2 and (y1 + y2) % _P == 0:
        return None
    if p == q:
        slope = (3 * x1 * x1) * pow(2 * y1, _P - 2, _P) % _P
    else:
        slope = (y2 - y1) * pow(x2 - x1, _P - 2, _P) % _P
    x3 = (slope * slope - x1 - x2) % _P
    return (x3, (slope * (x1 - x3) - y1) % _P)


def _multiply(scalar: int, point: Point = _G) -> Point:
    """Multiply a point by a scalar.

    Args:
        scalar: The multiplier, in [1, n).
        point: The point to multiply, defaulting to the generator.

    Returns:
        The resulting point.

    Raises:
        ValueError: If the result is the point at infinity.
    """
    result: Point | None = None
    addend: Point | None = point
    while scalar:
        if scalar & 1:
            result = _add(result, addend)
        addend = _add(addend, addend)
        scalar >>= 1
    if result is None:
        raise ValueError("Scalar multiplication produced the point at infinity")
    return result


def _compress(point: Point) -> bytes:
    """Serialize a point in SEC1 compressed form.

    Args:
        point: The point to serialize.

    Returns:
        33 bytes: a parity prefix followed by the x coordinate.
    """
    x, y = point
    return (b"\x03" if y & 1 else b"\x02") + x.to_bytes(32, "big")


def _derive_child(key: int, chain_code: bytes, index: int) -> tuple[int, bytes]:
    """Derive a child private key per BIP32 CKDpriv.

    Args:
        key: Parent private key.
        chain_code: Parent chain code.
        index: Child index; values >= 2**31 are hardened.

    Returns:
        The child private key and chain code.
    """
    if index >= _HARDENED:
        data = b"\x00" + key.to_bytes(32, "big")
    else:
        data = _compress(_multiply(key))
    digest = hmac.new(chain_code, data + index.to_bytes(4, "big"), sha512).digest()
    child = (int.from_bytes(digest[:32], "big") + key) % _N
    return child, digest[32:]


def _to_checksum_address(payload: bytes) -> str:
    """Encode 20 address bytes with an EIP-55 checksum.

    Args:
        payload: The raw 20-byte address.

    Returns:
        The 0x-prefixed, mixed-case address.
    """
    lowercase = payload.hex()
    digest = keccak256(lowercase.encode()).hex()
    return "0x" + "".join(
        char.upper() if int(digest[i], 16) > 7 else char
        for i, char in enumerate(lowercase)
    )


def eth_address(mnemonic: str, passphrase: str = "") -> str:
    """Derive the first Ethereum address for a BIP39 mnemonic.

    Uses the BIP44 path m/44'/60'/0'/0/0, matching what standard wallets
    show for a freshly imported seed phrase.

    Args:
        mnemonic: The BIP39 mnemonic phrase.
        passphrase: Optional BIP39 passphrase.

    Returns:
        The EIP-55 checksummed address.
    """
    seed = Mnemonic.to_seed(mnemonic, passphrase)
    digest = hmac.new(b"Bitcoin seed", seed, sha512).digest()
    key, chain_code = int.from_bytes(digest[:32], "big"), digest[32:]
    for index in _ETH_PATH:
        key, chain_code = _derive_child(key, chain_code, index)

    x, y = _multiply(key)
    uncompressed = x.to_bytes(32, "big") + y.to_bytes(32, "big")
    return _to_checksum_address(keccak256(uncompressed)[-20:])
