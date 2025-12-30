"""Common test configuration, constants, and utilities."""

# Test constants
WORDS_24 = 24
SPLIT_PARTS = 2


def assert_eth_addr(address):
    """Assert that address is a valid Ethereum address.
    """
    assert address.startswith("0x") and len(address) == 42
