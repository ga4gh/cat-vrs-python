"""Test that Cat-VRS Python model structures match Cat-VRS Schema"""

import json
from pathlib import Path

from ga4gh.cat_vrs import models as cat_vrs_models

ROOT_DIR = Path(__file__).parents[2]
CAT_VRS_SCHEMA_DIR = ROOT_DIR / "submodules" / "cat_vrs" / "schema" / "catvrs" / "json"
CAT_VRS_SCHEMA = {}

CAT_VRS_CONCRETE_CLASSES = set()
CAT_VRS_PRIMITIVES = set()

for f in CAT_VRS_SCHEMA_DIR.glob("*"):
    with f.open() as rf:
        cls_def = json.load(rf)

    cat_vrs_class = cls_def["title"]
    CAT_VRS_SCHEMA[cat_vrs_class] = cls_def

    if "properties" in cls_def:
        CAT_VRS_CONCRETE_CLASSES.add(cat_vrs_class)
    elif cls_def.get("type") in {"array", "int", "str"}:
        CAT_VRS_PRIMITIVES.add(cat_vrs_class)


def test_schema_models_exist():
    """Test that Cat-VRS Python covers the models defined by Cat-VRS"""
    for cat_vrs_class in CAT_VRS_CONCRETE_CLASSES | CAT_VRS_PRIMITIVES:
        assert getattr(cat_vrs_models, cat_vrs_class, False)


def test_schema_class_fields_are_valid():
    """Test that Cat-VRS Python model fields match the Cat-VRS specification"""
    for cat_vrs_class in CAT_VRS_CONCRETE_CLASSES:
        schema_fields = set(CAT_VRS_SCHEMA[cat_vrs_class]["properties"])
        pydantic_model = getattr(cat_vrs_models, cat_vrs_class)
        assert set(pydantic_model.model_fields) == schema_fields, cat_vrs_class


def test_model_keys_are_valid():
    """Test that digest keys on objects are valid and sorted"""
    for cat_vrs_class in CAT_VRS_CONCRETE_CLASSES:
        if (
            CAT_VRS_SCHEMA[cat_vrs_class].get("ga4ghDigest", {}).get("keys", None)
            is None
        ):
            continue

        pydantic_model = getattr(cat_vrs_models, cat_vrs_class)

        try:
            pydantic_model_digest_keys = pydantic_model.ga4gh.keys
        except AttributeError as e:
            raise AttributeError(cat_vrs_class) from e

        assert set(pydantic_model_digest_keys) == set(
            CAT_VRS_SCHEMA[cat_vrs_class]["ga4ghDigest"]["keys"]
        ), cat_vrs_class
        assert pydantic_model_digest_keys == sorted(
            pydantic_model.ga4gh.keys
        ), cat_vrs_class
