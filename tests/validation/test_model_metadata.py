"""Test model metadata against the Cat-VRS JSON schemas."""

import json
from pathlib import Path

import pytest
from pydantic import RootModel

from ga4gh.cat_vrs import CATVRS_VERSION, models, recipes
from ga4gh.core.metadata import Maturity

SCHEMA_DIR = Path(__file__).parents[2] / "submodules" / "cat_vrs" / "schema" / "cat-vrs"
SCHEMAS = (models, recipes)
JSON_DIR = SCHEMA_DIR / "json"

with (JSON_DIR / "CategoricalVariant").open() as schema_file:
    SPEC_VERSION = json.load(schema_file)["$id"].split("/")[-3]


def _model_params(abstract: bool):
    """Return model metadata discovered from JSON Schema files.

    :param abstract: Whether to return abstract models.
    :returns: Pytest parameters for matching Cat-VRS models and schemas.
    """
    params = []
    for schema_path in sorted(JSON_DIR.iterdir()):
        with schema_path.open() as schema_file:
            schema = json.load(schema_file)
        if schema.get("abstract", False) is not abstract:
            continue
        model = next(
            (
                getattr(module, schema_path.name, None)
                for module in SCHEMAS
                if hasattr(module, schema_path.name)
            ),
            None,
        )
        if model is not None:
            params.append(pytest.param(model, schema, id=schema_path.name))
    assert (
        params
    ), f"No {'abstract' if abstract else 'concrete'} Cat-VRS models discovered"
    return params


def test_cat_vrs_version_matches_source_schema():
    """The package version matches the authoritative Cat-VRS source schema."""
    assert CATVRS_VERSION == SPEC_VERSION


@pytest.mark.parametrize(("model", "schema"), _model_params(abstract=False))
def test_concrete_model_metadata(model, schema):
    """Concrete model metadata matches its published JSON Schema."""
    expected_schema_id = (
        f"https://w3id.org/ga4gh/schema/cat-vrs/{SPEC_VERSION}/json/"
        f"{model.__name__}"
    )
    assert model.schema_id() == expected_schema_id
    assert model.maturity() == Maturity(schema["maturity"])

    generated_schema = model.model_json_schema()
    assert generated_schema["$id"] == expected_schema_id
    assert generated_schema["maturity"] == schema["maturity"]
    assert "ga4gh" not in generated_schema


@pytest.mark.parametrize(("model", "schema"), _model_params(abstract=True))
def test_abstract_model_metadata(model, schema):
    """Abstract compatibility adapters expose published JSON Schema metadata."""
    assert model.maturity() == Maturity(schema["maturity"])

    generated_schema = model.model_json_schema()
    assert generated_schema["$id"] == schema["$id"]
    assert generated_schema["maturity"] == schema["maturity"]
    assert generated_schema["abstract"] is True
    if issubclass(model, RootModel):
        assert generated_schema["discriminator"]["propertyName"] == "type"
        assert len(generated_schema["oneOf"]) == len(schema["oneOf"])
