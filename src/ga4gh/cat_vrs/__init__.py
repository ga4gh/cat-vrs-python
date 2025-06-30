"""Package for Cat-VRS Python implementation"""

from importlib.metadata import PackageNotFoundError, version

from . import models, recipes

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: nocover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


CATVRS_VERSION = "1.0.0"

__all__ = [
    "CATVRS_VERSION",
    "__version__",
    "models",
    "recipes",
]
