"""Test model metadata against the Cat-VRS source and JSON schemas."""

import json
from pathlib import Path

import pytest
import yaml

from ga4gh.cat_vrs import CATVRS_VERSION, models, recipes
from ga4gh.core.metadata import Maturity

SCHEMA_DIR = Path(__file__).parents[2] / "submodules" / "cat_vrs" / "schema" / "cat-vrs"
SCHEMAS = (
    (models, SCHEMA_DIR / "cat-vrs-source.yaml"),
    (recipes, SCHEMA_DIR / "recipes-source.yaml"),
)
JSON_DIR = SCHEMA_DIR / "json"

with (SCHEMA_DIR / "cat-vrs-source.yaml").open() as source_file:
    CATVRS_SOURCE = yaml.safe_load(source_file)

SPEC_VERSION = CATVRS_SOURCE["$id"].split("/")[-2]


def _model_params():
    """Return model metadata discovered from both source YAML files."""
    params = []
    for model_module, source_path in SCHEMAS:
        with source_path.open() as source_file:
            definitions = yaml.safe_load(source_file)["$defs"]
        for name, definition in definitions.items():
            model = getattr(model_module, name)
            with (JSON_DIR / name).open() as schema_file:
                schema = json.load(schema_file)
            params.append(pytest.param(model, definition, schema, id=name))
    assert params, "No concrete Cat-VRS models discovered"
    return params


def test_cat_vrs_version_matches_source_schema():
    """The package version matches the authoritative Cat-VRS source schema."""
    assert CATVRS_VERSION == SPEC_VERSION


@pytest.mark.parametrize(("model", "definition", "schema"), _model_params())
def test_model_metadata(model, definition, schema):
    """Model metadata matches its source and generated JSON Schemas."""
    expected_schema_id = (
        f"https://w3id.org/ga4gh/schema/cat-vrs/{SPEC_VERSION}/json/"
        f"{model.__name__}"
    )
    assert model.schema_id() == expected_schema_id
    assert model.maturity() == Maturity(definition["maturity"])

    generated_schema = model.model_json_schema()
    assert generated_schema["$id"] == expected_schema_id
    assert generated_schema["maturity"] == schema["maturity"]
    assert "ga4gh" not in generated_schema
