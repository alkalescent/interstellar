"""Keccak-256, as used by Ethereum for address derivation.

Ethereum uses original Keccak padding (0x01), not the NIST SHA-3 padding
(0x06) that :mod:`hashlib` provides, so ``hashlib.sha3_256`` cannot be
substituted here.

Implemented in pure Python so the package has no compiled dependency. See
``tests/test_keccak.py`` for the published test vectors this is checked
against, plus a differential comparison with a reference implementation.
"""

from __future__ import annotations

# Round constants for the iota step, Keccak-f[1600], 24 rounds.
_ROUND_CONSTANTS: tuple[int, ...] = (
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
)  # fmt: skip

# Rotation offsets for the rho step, indexed [x][y].
_ROTATION_OFFSETS: tuple[tuple[int, ...], ...] = (
    (0, 36, 3, 41, 18),
    (1, 44, 10, 45, 2),
    (62, 6, 43, 15, 61),
    (28, 55, 25, 21, 56),
    (27, 20, 39, 8, 14),
)

_MASK64 = (1 << 64) - 1

# Keccak-256 absorbs 1088 bits at a time and emits 256.
_RATE_BYTES = 136
_DIGEST_BYTES = 32


def _rotl64(value: int, shift: int) -> int:
    """Rotate a 64-bit word left.

    Args:
        value: The word to rotate.
        shift: Number of bits to rotate by.

    Returns:
        The rotated word.
    """
    if not shift:
        return value
    return ((value << shift) | (value >> (64 - shift))) & _MASK64


def _permute(state: list[list[int]]) -> list[list[int]]:
    """Apply the Keccak-f[1600] permutation in place.

    Args:
        state: 5x5 matrix of 64-bit lanes.

    Returns:
        The permuted state.
    """
    for round_constant in _ROUND_CONSTANTS:
        # theta
        parity = [
            state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4]
            for x in range(5)
        ]
        delta = [
            parity[(x - 1) % 5] ^ _rotl64(parity[(x + 1) % 5], 1) for x in range(5)
        ]
        for x in range(5):
            for y in range(5):
                state[x][y] ^= delta[x]

        # rho and pi
        scratch = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                scratch[y][(2 * x + 3 * y) % 5] = _rotl64(
                    state[x][y], _ROTATION_OFFSETS[x][y]
                )

        # chi
        for x in range(5):
            for y in range(5):
                state[x][y] = scratch[x][y] ^ (
                    (~scratch[(x + 1) % 5][y] & _MASK64) & scratch[(x + 2) % 5][y]
                )

        # iota
        state[0][0] ^= round_constant
    return state


def keccak256(data: bytes) -> bytes:
    """Compute the Keccak-256 digest of a byte string.

    Args:
        data: Message to hash.

    Returns:
        The 32-byte digest.
    """
    state = [[0] * 5 for _ in range(5)]

    padded = bytearray(data)
    padded.append(0x01)
    padded.extend(b"\x00" * ((-len(padded)) % _RATE_BYTES))
    padded[-1] |= 0x80

    lanes = _RATE_BYTES // 8
    for offset in range(0, len(padded), _RATE_BYTES):
        block = padded[offset : offset + _RATE_BYTES]
        for i in range(lanes):
            state[i % 5][i // 5] ^= int.from_bytes(block[i * 8 : (i + 1) * 8], "little")
        state = _permute(state)

    squeezed = b"".join(
        state[i % 5][i // 5].to_bytes(8, "little") for i in range(lanes)
    )
    return squeezed[:_DIGEST_BYTES]
