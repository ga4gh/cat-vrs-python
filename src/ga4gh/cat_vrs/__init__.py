"""Package for Cat-VRS Python implementation"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version

from . import models, recipes
from .metadata import CatVRSMetadataMixin
from .version import CATVRS_VERSION

try:
    __version__ = package_version(__name__)
except PackageNotFoundError:  # pragma: nocover
    __version__ = "unknown"
finally:
    del package_version, PackageNotFoundError


__all__ = [
    "CATVRS_VERSION",
    "CatVRSMetadataMixin",
    "__version__",
    "models",
    "recipes",
]
