"""Package initialization with dynamic version and public API exports."""

from interstellar.tools import BIP39, SLIP39

try:
    # Written by the hatch-vcs build hook, so Nuitka binaries compile it in
    from interstellar._version import __version__
except ImportError:  # Source tree that was never built or installed
    __version__ = "0.0.0"

__all__ = ["BIP39", "SLIP39", "__version__"]
