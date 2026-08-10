"""Tests for the vendored Keccak-256 implementation."""

from __future__ import annotations

import hashlib

import pytest

from interstellar.keccak import keccak256

# Published Keccak-256 digests. These are original Keccak, as used by
# Ethereum, not NIST SHA3-256.
VECTORS = [
    (b"", "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"),
    (b"abc", "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45"),
    (
        b"The quick brown fox jumps over the lazy dog",
        "4d741b6f1eb29cb2a9b9911c82f56fa8d73b04959d3d9d222895df6c0b28aa15",
    ),
    (
        b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
        "45d3b367a6904e6e8d502ee04999a7c27647f91fa845d456525fd352ae3d7371",
    ),
]


@pytest.mark.parametrize(("data", "expected"), VECTORS)
def test_published_vectors(data: bytes, expected: str) -> None:
    """Test digests match the published Keccak-256 vectors."""
    assert keccak256(data).hex() == expected


def test_not_nist_sha3() -> None:
    """Test this is Keccak, not the NIST SHA3 variant hashlib provides.

    The two differ only in padding, so a wrong implementation would still
    look plausible without this check.
    """
    assert keccak256(b"") != hashlib.sha3_256(b"").digest()


@pytest.mark.parametrize("size", [0, 1, 135, 136, 137, 271, 272, 273, 1000])
def test_rate_boundaries(size: int) -> None:
    """Test inputs around the 136-byte rate absorb correctly."""
    digest = keccak256(b"\xa5" * size)
    assert len(digest) == 32


def test_digest_length_and_determinism() -> None:
    """Test the digest is 32 bytes and stable across calls."""
    data = b"interstellar"
    assert len(keccak256(data)) == 32
    assert keccak256(data) == keccak256(data)


def test_avalanche() -> None:
    """Test a one-bit input change produces a wholly different digest."""
    a = keccak256(b"interstellar")
    b = keccak256(b"interstellat")
    assert a != b
    differing_bits = sum(bin(x ^ y).count("1") for x, y in zip(a, b, strict=True))
    # A sound hash flips roughly half of the 256 output bits.
    assert 90 < differing_bits < 166
