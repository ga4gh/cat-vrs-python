"""Provide metadata mixins for Cat-VRS models."""

from ga4gh.cat_vrs.version import CATVRS_VERSION
from ga4gh.core.metadata import GKSMetadataMixin


class CatVRSMetadataMixin(GKSMetadataMixin):
    """Provide metadata for a concrete Cat-VRS model."""

    _product_name = "cat-vrs"
    _product_version = CATVRS_VERSION
