"""Test that Cat VRS-Python Pydantic models match corresponding JSON schemas"""

import json
from enum import Enum
from pathlib import Path

import pytest
import yaml
from ga4gh.cat_vrs import models, recipes
from pydantic import BaseModel


class CatVrsSchema(str, Enum):
    """Enum for Cat VRS schema"""

    CAT_VRS = "cat_vrs"
    RECIPES = "recipes"


class CatVrsSchemaMapping(BaseModel):
    """Model for representing Cat-VRS Schema concrete classes, primitives, and schema"""

    base_classes: set = set()
    concrete_classes: set = set()
    primitives: set = set()
    cat_vrs_schema: dict = {}


def _update_cat_vrs_schema_mapping(
    f_path: Path, cat_vrs_schema_mapping: CatVrsSchemaMapping
) -> None:
    """Update ``cat_vrs_schema_mapping`` properties

    :param f_path: Path to JSON Schema file
    :param cat_vrs_schema_mapping: Cat-VRS schema mapping to update
    """
    with f_path.open() as rf:
        cls_def = json.load(rf)

    spec_class = cls_def["title"]
    cat_vrs_schema_mapping.cat_vrs_schema[spec_class] = cls_def

    if "properties" in cls_def:
        cat_vrs_schema_mapping.concrete_classes.add(spec_class)
    elif cls_def.get("type") in {"array", "integer", "string"}:
        cat_vrs_schema_mapping.primitives.add(spec_class)
    else:
        cat_vrs_schema_mapping.base_classes.add(spec_class)


CAT_VRS_SCHEMA_MAPPING = {schema: CatVrsSchemaMapping() for schema in CatVrsSchema}
SUBMODULES_DIR = (
    Path(__file__).parents[2] / "submodules" / "cat_vrs" / "schema" / "cat-vrs"
)

with (SUBMODULES_DIR / "cat-vrs-source.yaml").open() as f:
    cat_vrs_data = yaml.safe_load(f)
    cat_vrs_defs_keys = cat_vrs_data["$defs"].keys()

for f in (SUBMODULES_DIR / "json").glob("*"):
    if f.name.startswith("example"):
        continue

    schema = (
        CatVrsSchema.CAT_VRS if f.name in cat_vrs_defs_keys else CatVrsSchema.RECIPES
    )
    _update_cat_vrs_schema_mapping(f, CAT_VRS_SCHEMA_MAPPING[schema])


@pytest.mark.parametrize(
    ("cat_vrs_schema", "pydantic_models"),
    [
        (CatVrsSchema.CAT_VRS, models),
        (CatVrsSchema.RECIPES, recipes),
    ],
)
def test_schema_models_in_pydantic(cat_vrs_schema, pydantic_models):
    """Ensure that each schema model has corresponding Pydantic model"""
    mapping = CAT_VRS_SCHEMA_MAPPING[cat_vrs_schema]
    for schema_model in (
        mapping.base_classes | mapping.concrete_classes | mapping.primitives
    ):
        assert getattr(pydantic_models, schema_model, False), schema_model


@pytest.mark.parametrize(
    ("cat_vrs_schema", "pydantic_models"),
    [
        (CatVrsSchema.CAT_VRS, models),
        (CatVrsSchema.RECIPES, recipes),
    ],
)
def test_schema_class_fields(cat_vrs_schema, pydantic_models):
    """Check that each schema model properties exist and are required in corresponding
    Pydantic model, and validate required properties
    """
    mapping = CAT_VRS_SCHEMA_MAPPING[cat_vrs_schema]
    for schema_model in mapping.concrete_classes:
        schema_properties = mapping.cat_vrs_schema[schema_model]["properties"]
        pydantic_model = getattr(pydantic_models, schema_model)
        assert set(pydantic_model.model_fields) == set(schema_properties), schema_model

        required_schema_fields = set(mapping.cat_vrs_schema[schema_model]["required"])

        for prop, property_def in schema_properties.items():
            pydantic_model_field_info = pydantic_model.model_fields[prop]
            pydantic_field_required = pydantic_model_field_info.is_required()

            if prop in required_schema_fields:
                if prop != "type":
                    assert pydantic_field_required, f"{pydantic_model}.{prop}"
            else:
                assert not pydantic_field_required, f"{pydantic_model}.{prop}"

            if "description" in property_def:
                assert property_def["description"].replace(
                    "'", '"'
                ) == pydantic_model_field_info.description.replace(
                    "'", '"'
                ), f"{pydantic_model}.{prop}"
            else:
                assert (
                    pydantic_model_field_info.description is None
                ), f"{pydantic_model}.{prop}"
