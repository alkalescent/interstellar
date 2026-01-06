"""Package initialization with dynamic version and public API exports."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_version
from pathlib import Path

# Get package name dynamically from directory structure
PACKAGE_NAME = Path(__file__).parent.name

try:
    __version__ = get_version(PACKAGE_NAME)
except PackageNotFoundError:
    __version__ = "0.0.0"

# Re-export public API
from interstellar.tools import BIP39, SLIP39  # noqa: E402

__all__ = ["BIP39", "SLIP39", "__version__", "PACKAGE_NAME"]
