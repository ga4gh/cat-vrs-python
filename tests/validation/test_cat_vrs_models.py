"""Test Cat VRS Pydantic models"""

from copy import deepcopy

import pytest
from ga4gh.cat_vrs import models, recipes
from ga4gh.core.models import (
    Coding,
    MappableConcept,
    code,
)

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
    return models.CopyChangeConstraint(copyChange="gain")


@pytest.fixture(scope="module")
def members_and_name():
    """Create test fixture for members and name"""
    return {"members": ["variation.json#/1"], "name": "dummy"}


@pytest.fixture(scope="module")
def defining_loc_constr():
    """Create test fixture for defining location constraint"""
    return models.DefiningLocationConstraint(
        relations=[
            MappableConcept(
                primaryCoding=Coding(
                    code=code(models.Relation.LIFTOVER_TO.value),
                    system="ga4gh-gks-term:allele-relation",
                )
            )
        ],
        location="location.json#/1",
        matchCharacteristic=MappableConcept(name="test"),
    )


def test_copy_count_constraint():
    """Test the CopyCountConstraint validator"""
    # Valid Copy Count Constraint
    assert models.CopyCountConstraint(copies=2)

    # Invalid Copy Count Constraint
    with pytest.raises(
        ValueError,
        match="The first integer must be less than or equal to the second integer.",
    ):
        models.CopyCountConstraint(copies=[3, 2])


def test_copy_change_constraint():
    """Test the CopyChangeConstraint validator"""
    # Valid Copy Change
    assert models.CopyChangeConstraint(copyChange="loss")

    # Invalid Copy Change
    with pytest.raises(
        ValueError,
        match="Input should be 'complete genomic loss', 'high-level loss', 'low-level loss', 'loss', 'regional base ploidy', 'gain', 'low-level gain' or 'high-level gain'",
    ):
        models.CopyChangeConstraint(copyChange="0030069")


def test_protein_sequence_consequence(defining_loc_constr, members_and_name):
    """Test the ProteinSequenceConsequence validator"""
    # Valid PSC
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSLATION_OF.value),
                            system="http://www.sequenceontology.org",
                        )
                    )
                ],
                allele=DUMMY_ALLELE_IRI,
            )
        )
    ]
    assert recipes.ProteinSequenceConsequence(**valid_params)

    # Invalid PSC: Constraint is NOT DefiningAlleleContext
    err_msg = "Unable to find at least one constraint that is a"
    invalid_params = deepcopy(members_and_name)
    invalid_params["constraints"] = [models.Constraint(root=defining_loc_constr)]
    with pytest.raises(ValueError, match=err_msg):
        assert recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: No relations defined
    invalid_params = deepcopy(members_and_name)
    invalid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations(is_empty_list=False))
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: Empty list of relations
    invalid_params = deepcopy(members_and_name)
    invalid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations(is_empty_list=True))
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: relations does not use primaryCoding
    invalid_params = deepcopy(members_and_name)
    invalid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[MappableConcept(name=models.Relation.LIFTOVER_TO.value)],
                allele=DUMMY_ALLELE_IRI,
            )
        )
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: relations has 0 'translation_of'
    invalid_params = deepcopy(members_and_name)
    invalid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.LIFTOVER_TO.value),
                            system="http://www.sequenceontology.org",
                        )
                    )
                ],
                allele=DUMMY_ALLELE_IRI,
            )
        )
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)

    # Invalid PSC: relations has > 1 'translation_of'
    invalid_params = deepcopy(members_and_name)
    invalid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSLATION_OF.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSLATION_OF.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                ],
                allele=DUMMY_ALLELE_IRI,
            )
        )
    ]
    with pytest.raises(ValueError, match=err_msg):
        recipes.ProteinSequenceConsequence(**invalid_params)


def test_canonical_allele(defining_loc_constr, members_and_name):
    """Test the CanonicalAllele validator"""
    # Valid CanonicalAllele
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.LIFTOVER_TO.value),
                            system="ga4gh-gks-term:allele-relation",
                        )
                    ),
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSCRIBED_TO.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                ],
                allele=DUMMY_ALLELE_IRI,
            )
        )
    ]
    assert recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: Constraint is NOT DefiningAlleleContext
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [models.Constraint(root=defining_loc_constr)]
    with pytest.raises(
        ValueError, match="Constraint must be a `DefiningAlleleConstraint`."
    ):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: No relations defined
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations(is_empty_list=False))
    ]
    with pytest.raises(ValueError, match="`relations` is required."):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: Empty list of relations
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations(is_empty_list=True))
    ]
    with pytest.raises(ValueError, match="`relations` is required."):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: No 'liftover_to'
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSCRIBED_TO.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSCRIBED_TO.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                ],
                allele=DUMMY_ALLELE_IRI,
            )
        )
    ]
    with pytest.raises(
        ValueError,
        match="Must contain exactly one relation where `primaryCoding.code` is 'liftover_to'.",
    ):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: > 1 'liftover_to'
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.LIFTOVER_TO.value),
                            system="ga4gh-gks-term:allele-relation",
                        )
                    ),
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.LIFTOVER_TO.value),
                            system="ga4gh-gks-term:allele-relation",
                        )
                    ),
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSCRIBED_TO.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                ],
                allele=DUMMY_ALLELE_IRI,
            )
        )
    ]
    with pytest.raises(
        ValueError,
        match="Must contain exactly one relation where `primaryCoding.code` is 'liftover_to'.",
    ):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: No 'transcribed_to'
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.LIFTOVER_TO.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSLATION_OF.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                ],
                allele=DUMMY_ALLELE_IRI,
            )
        )
    ]
    with pytest.raises(
        ValueError,
        match="Must contain exactly one relation where `primaryCoding.code` is 'liftover_to' and `primaryCoding.system` is 'ga4gh-gks-term:allele-relation'.",
    ):
        recipes.CanonicalAllele(**valid_params)

    # Invalid CanonicalAllele: > 1 'transcribed_to'
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(
            root=models.DefiningAlleleConstraint(
                relations=[
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.LIFTOVER_TO.value),
                            system="ga4gh-gks-term:allele-relation",
                        )
                    ),
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSCRIBED_TO.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                    MappableConcept(
                        primaryCoding=Coding(
                            code=code(models.Relation.TRANSCRIBED_TO.value),
                            system="http://www.sequenceontology.org",
                        )
                    ),
                ],
                allele=DUMMY_ALLELE_IRI,
            )
        )
    ]
    with pytest.raises(
        ValueError,
        match="Must contain exactly one relation where `primaryCoding.code` is 'transcribed_to'.",
    ):
        recipes.CanonicalAllele(**valid_params)


def test_categorical_cnv(members_and_name, defining_loc_constr, copy_change_constr):
    """Test the CategoricalCnv validator"""
    # Valid CategoricalCnv with CopyChangeConstraint
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(root=defining_loc_constr),
        models.Constraint(root=copy_change_constr),
    ]
    assert recipes.CategoricalCnv(**valid_params)

    # Valid CategoricalCnv with CopyCountConstraint
    valid_params = deepcopy(members_and_name)
    valid_params["constraints"] = [
        models.Constraint(root=defining_loc_constr),
        models.Constraint(root=models.CopyCountConstraint(copies=[1, 2])),
    ]
    assert recipes.CategoricalCnv(**valid_params)

    # Invalid CategoricalCnv: No DefiningLocationConstraint
    invalid_params = deepcopy(members_and_name)
    invalid_params["constraints"] = [
        models.Constraint(root=def_allele_constr_empty_relations()),
        copy_change_constr,
    ]
    with pytest.raises(
        ValueError,
        match="Must contain a `DefiningLocationConstraint` with at least one relation where `primaryCoding.code` is 'liftover_to'.",
    ):
        recipes.CategoricalCnv(**invalid_params)

    # Invalid CategoricalCnv: DefiningLocationConstraint does not have 'liftover_to'
    invalid_params = deepcopy(members_and_name)
    invalid_defining_loc_constr = defining_loc_constr.model_copy(deep=True)
    invalid_defining_loc_constr.relations = [
        MappableConcept(
            primaryCoding=Coding(
                code=code(models.Relation.TRANSCRIBED_TO.value),
                system="ga4gh-gks-term:allele-relation",
            )
        )
    ]
    invalid_params["constraints"] = [
        invalid_defining_loc_constr,
        copy_change_constr,
    ]
    with pytest.raises(
        ValueError,
        match="`DefiningLocationConstraint` found, but must contain at least one relation where `primaryCoding.code` is 'liftover_to' and `primaryCoding.system` is 'ga4gh-gks-term:allele-relation'.",
    ):
        recipes.CategoricalCnv(**invalid_params)

    # Invalid No CopyCountConstraint and no CopyChangeConstraint provided
    invalid_params["constraints"] = [
        invalid_defining_loc_constr,
        defining_loc_constr,
    ]
    with pytest.raises(
        ValueError,
        match="Must contain either a `CopyCountConstraint` or `CopyChangeConstraint`.",
    ):
        recipes.CategoricalCnv(**invalid_params)
