"""Test Cat VRS Pydantic models"""

from copy import deepcopy

import pytest
from ga4gh.cat_vrs import models, recipes
from ga4gh.core.models import (
    MappableConcept,
    code,
)
from ga4gh.vrs.models import CopyChange

DUMMY_ALLELE_IRI = "allele.json#/1"  # Valid IRI but does not reference anything


def def_allele_constr_empty_relations(
    is_empty_list=True,
) -> models.DefiningAlleleConstraint:
    """Return DefiningAlleleConstraint with either empty relations or null relations

    :param is_empty_list: ``True`` if relations should be empty list. Otherwise,
        relations will be null
    """
    return models.DefiningAlleleConstraint(
        relations=[] if is_empty_list else None, allele="allele.json#/1"
    )


@pytest.fixture(scope="module")
def copy_change_constr():
    """Create test fixture for copy change constraint"""
    return models.CopyChangeConstraint(copyChange=CopyChange.EFO_0030069.value)


@pytest.fixture(scope="module")
def members():
    """Create test fixture for members"""
    return {"members": ["variation.json#/1"]}


@pytest.fixture(scope="module")
def defining_loc_constr():
    """Create test fixture for defining location constraint"""
    return models.DefiningLocationConstraint(
        relations=[
            MappableConcept(primaryCode=code(models.Relation.LIFTOVER_TO.value))
        ],
        location="location.json#/1",
        matchCharacteristic=MappableConcept(label="test"),
    )


def test_copy_change_constraint():
    """Test the CopyChangeConstraint validator"""
    # Valid Copy Change
    assert models.CopyChangeConstraint(copyChange=CopyChange.EFO_0030069.value)

    # Invalid Copy Change
    with pytest.raises(ValueError, match="copyChange, 0030069, not one of"):
        models.CopyChangeConstraint(copyChange="0030069")


def test_protein_sequence_consequence(defining_loc_constr, members):
    """Test the ProteinSequenceConsequence validator"""
    # Valid PSC
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSLATES_FROM.value)
                    )
                ],
                allele=DUMMY_ALLELE_IRI
            )
        )
    ]
    assert recipes.ProteinSequenceConsequence(**valid_params)

    # Invalid PSC: Constraint is NOT DefiningAlleleContext
    err_msg = "Unable to find at least one constraint that is a"
    invalid_params = deepcopy(members)
    invalid_params["constraints"] = [models.Constraint(root=defining_loc_constr)]
    with pytest.raises(ValueError, match=err_msg):
        assert recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: No relations defined
    invalid_params = deepcopy(members)
    invalid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations(is_empty_list=False))
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: Empty list of relations
    invalid_params = deepcopy(members)
    invalid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations(is_empty_list=True))
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: relations does not use primaryCode
    invalid_params = deepcopy(members)
    invalid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[MappableConcept(label=models.Relation.LIFTOVER_TO.value)],
                allele=DUMMY_ALLELE_IRI
            )
        )
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: relations has 0 'translates_from'
    invalid_params = deepcopy(members)
    invalid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(primaryCode=code(models.Relation.LIFTOVER_TO.value))
                ],
                allele=DUMMY_ALLELE_IRI
            )
        )
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: relations has > 1 'translates_from'
    invalid_params = deepcopy(members)
    invalid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSLATES_FROM.value)
                    ),
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSLATES_FROM.value)
                    ),
                ],
                allele=DUMMY_ALLELE_IRI
            )
        )
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)


def test_canonical_allele(defining_loc_constr, members):
    """Test the CanonicalAllele validator"""
    # Valid CanonicalAllele
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCode=code(models.Relation.LIFTOVER_TO.value)
                    ),
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSCRIBES_TO.value)
                    ),
                ],
                allele=DUMMY_ALLELE_IRI
            )
        )
    ]
    assert recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: Constraint is NOT DefiningAlleleContext
    valid_params = deepcopy(members)
    valid_params["constraints"] = [models.Constraint(root=defining_loc_constr)]
    with pytest.raises(
        ValueError, match="Constraint must be a `DefiningAlleleConstraint`."
    ):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: No relations defined
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations(is_empty_list=False))
    ]
    with pytest.raises(ValueError, match="`relations` is required."):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: Empty list of relations
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations(is_empty_list=True))
    ]
    with pytest.raises(ValueError, match="`relations` is required."):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: No 'liftover_to'
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSCRIBES_TO.value)
                    ),
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSCRIBES_TO.value)
                    ),
                ],
                allele=DUMMY_ALLELE_IRI
            )
        )
    ]
    with pytest.raises(
        ValueError,
        match="Must contain exactly one relation where `primaryCode` is 'liftover_to'.",
    ):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: > 1 'liftover_to'
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCode=code(models.Relation.LIFTOVER_TO.value)
                    ),
                    MappableConcept(
                        primaryCode=code(models.Relation.LIFTOVER_TO.value)
                    ),
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSCRIBES_TO.value)
                    ),
                ],
                allele=DUMMY_ALLELE_IRI
            )
        )
    ]
    with pytest.raises(
        ValueError,
        match="Must contain exactly one relation where `primaryCode` is 'liftover_to'.",
    ):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: No 'transcribes_to'
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCode=code(models.Relation.LIFTOVER_TO.value)
                    ),
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSLATES_FROM.value)
                    ),
                ],
                allele=DUMMY_ALLELE_IRI
            )
        )
    ]
    with pytest.raises(
        ValueError,
        match="Must contain exactly one relation where `primaryCode` is 'transcribes_to'.",
    ):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: > 1 'transcribes_to'
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCode=code(models.Relation.LIFTOVER_TO.value)
                    ),
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSCRIBES_TO.value)
                    ),
                    MappableConcept(
                        primaryCode=code(models.Relation.TRANSCRIBES_TO.value)
                    ),
                ],
                allele=DUMMY_ALLELE_IRI
            )
        )
    ]
    with pytest.raises(
        ValueError,
        match="Must contain exactly one relation where `primaryCode` is 'transcribes_to'.",
    ):
        recipes.CanonicalAllele(**valid_params)


def test_categorical_cnv(members, defining_loc_constr, copy_change_constr):
    """Test the CategoricalCnv validator"""
    # Valid CategoricalCnv with CopyChangeConstraint
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(root=defining_loc_constr),
        models.Constraint(root=copy_change_constr),
    ]
    assert recipes.CategoricalCnv(**valid_params)

    # Valid CategoricalCnv with CopyCountConstraint
    valid_params = deepcopy(members)
    valid_params["constraints"] = [
        models.Constraint(root=defining_loc_constr),
        models.Constraint(root=models.CopyCountConstraint(copies=[1, 2])),
    ]
    assert recipes.CategoricalCnv(**valid_params)

    # Invalid CategoricalCnv: No DefiningLocationConstraint
    invalid_params = deepcopy(members)
    invalid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations()),
        copy_change_constr,
    ]
    with pytest.raises(
        ValueError,
        match="Must contain a `DefiningLocationConstraint` with at least one relation where `primaryCode` is 'liftover_to'.",
    ):
        recipes.CategoricalCnv(**invalid_params)

    # Invalid CategoricalCnv: DefiningLocationConstraint does not have 'liftover_to'
    invalid_params = deepcopy(members)
    invalid_defining_loc_constr = defining_loc_constr.copy(deep=True)
    invalid_defining_loc_constr.relations = [
        MappableConcept(primaryCode=code(models.Relation.TRANSCRIBES_TO.value))
    ]
    invalid_params["constraints"] = [
        invalid_defining_loc_constr,
        copy_change_constr,
    ]
    with pytest.raises(
        ValueError,
        match="Must contain a `DefiningLocationConstraint` with at least one relation where `primaryCode` is 'liftover_to'.",
    ):
        recipes.CategoricalCnv(**invalid_params)

    # Invalid No CopyCountConstraint or CopyChangeConstraint
    invalid_params["constraints"] = [
        invalid_defining_loc_constr,
        defining_loc_constr,
    ]
    with pytest.raises(
        ValueError,
        match="Must contain either a `CopyCountConstraint` or `CopyChangeConstraint`.",
    ):
        recipes.CategoricalCnv(**invalid_params)
