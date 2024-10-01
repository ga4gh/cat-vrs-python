"""Define Pydantic models for GA4GH categorical variation objects.

See the `CatVar page <https://www.ga4gh.org/product/categorical-variation-catvar/>`_ on
the GA4GH website for more information.
"""

import logging
from enum import Enum

from ga4gh.cat_vrs.core_models import (
    CategoricalVariant,
    Constraint,
    DefiningContextConstraint,
    Relation,
)
from pydantic import BaseModel, field_validator


class CatVrsType(str, Enum):
    """Define CatVRS types"""

    PROTEIN_SEQ_CONS = "ProteinSequenceConsequence"
    CANONICAL_ALLELE = "CanonicalAllele"
    CATEGORICAL_CNV = "CategoricalCnv"
    DESCRIBED_VAR = "DescribedVariation"
    NUMBER_COUNT = "NumberCount"
    NUMBER_CHANGE = "NumberChange"
    QUANTITY_VARIANCE = "QuantityVariance"


class ProteinSequenceConsequenceProperties(BaseModel):
    """Cat-VRS Constraints found in Protein Sequence Consequences."""

    constraints: DefiningContextConstraint

    @field_validator("constraints")
    @classmethod
    def validate_constraints(
        cls, v: DefiningContextConstraint
    ) -> DefiningContextConstraint:
        """Validate constraints property

        :param v: Constraints property to validate
        :return: Constraints property
        """
        if v.relations and Relation.CODON_TRANSLATION not in v.relations:
            logging.warning(
                "`constraints.relations` is missing the following relation: %s.",
                Relation.CODON_TRANSLATION.value,
            )
        return v


class ProteinSequenceConsequence(
    ProteinSequenceConsequenceProperties, CategoricalVariant
):
    """A change that occurs in a protein sequence as a result of genomic changes. Due to
    the degenerate nature of the genetic code, there are often several genomic changes
    that can cause a protein sequence consequence.
    The protein sequence consequence, like a :ref:`CanonicalAllele`, is defined by an
    `Allele <https://vrs.ga4gh.org/en/2.x/concepts/MolecularVariation/Allele.html#>`_
    that is representative of a collection of congruent Protein Alleles that share the
    same altered codon(s).
    """


class CanonicalAlleleProperties(BaseModel):
    """Cat-VRS Constraints found in Canonical Alleles."""

    constraints: DefiningContextConstraint

    @field_validator("constraints")
    @classmethod
    def validate_constraints(
        cls, v: DefiningContextConstraint
    ) -> DefiningContextConstraint:
        """Validate constraints property

        :param v: Constraints property to validate
        :return: Constraints property
        """
        if v.relations:
            required_relations = {
                Relation.SEQUENCE_LIFTOVER,
                Relation.TRANSCRIPT_PROJECTION,
            }
            relations = set(v.relations)

            if not required_relations.issubset(relations):
                missing_relations = required_relations - relations
                logging.warning(
                    "`constraints.relations` is missing the following relations: %s.",
                    missing_relations,
                )
        return v


class CanonicalAllele(CanonicalAlleleProperties, CategoricalVariant):
    """A canonical allele is defined by an
    `Allele <https://vrs.ga4gh.org/en/2.x/concepts/MolecularVariation/Allele.html#>`_
    that is representative of a collection of congruent Alleles, each of which depict
    the same nucleic acid change on different underlying reference sequences. Congruent
    representations of an Allele often exist across different genome assemblies and
    associated cDNA transcript representations.
    """


class CategoricalCnvProperties(BaseModel):
    """Cat-VRS Constraints found in CategoricalCnvs."""

    constraints: Constraint

    @field_validator("constraints")
    @classmethod
    def validate_constraints(
        cls, v: DefiningContextConstraint
    ) -> DefiningContextConstraint:
        """Validate constraints property

        :param v: Constraints property to validate
        :return: Constraints property
        """
        if v.relations and Relation.SEQUENCE_LIFTOVER not in v.relations:
            logging.warning(
                "`constraints.relations` is missing the following relation: %s.",
                Relation.SEQUENCE_LIFTOVER.value,
            )
        return v


class CategoricalCnv(CategoricalCnvProperties, CategoricalVariant):
    """A representation of the constraints for matching knowledge about CNVs."""
