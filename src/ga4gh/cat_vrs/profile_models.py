"""Define Pydantic models for GA4GH categorical variation objects.

See the `CatVar page <https://www.ga4gh.org/product/categorical-variation-catvar/>`_ on
the GA4GH website for more information.
"""

from enum import Enum

from ga4gh.cat_vrs.core_models import (
    CategoricalVariant,
    Constraint,
    CopyChangeConstraint,
    CopyCountConstraint,
    DefiningContextConstraint,
    Relation,
)
from pydantic import BaseModel, Field, field_validator


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

    constraints: list[Constraint] = Field(..., min_length=1)

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[Constraint]) -> list[Constraint]:
        """Validate constraints property

        :param v: Constraints property to validate
        :raises ValueError: If none of the ``relations`` contains
            ``Relation.CODON_TRANSLATION.value`` exactly once.
        :return: Constraints property
        """
        if not any(
            constraint.relations.count(Relation.CODON_TRANSLATION) == 1
            for constraint in v
        ):
            err_msg = f"At least one `relations` in `constraints` must contain `{Relation.CODON_TRANSLATION.value}` exactly once."
            raise ValueError(err_msg)

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

    constraints: list[Constraint] = Field(..., min_length=1)

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[Constraint]) -> list[Constraint]:
        """Validate constraints property

        :param v: Constraints property to validate
        :raises ValueError: If none of the ``relations`` contains both
            ``Relation.SEQUENCE_LIFTOVER`` and ``Relation.TRANSCRIPT_PROJECTION``
            exactly once.
        :return: Constraints property
        """
        if not any(
            (
                constraint.relations.count(Relation.SEQUENCE_LIFTOVER) == 1
                and constraint.relations.count(Relation.TRANSCRIPT_PROJECTION) == 1
            )
            for constraint in v
        ):
            err_msg = f"At least one `relations` in `constraints` must contain {Relation.SEQUENCE_LIFTOVER} and {Relation.TRANSCRIPT_PROJECTION} exactly once."
            raise ValueError(err_msg)

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

    constraints: list[Constraint] = Field(..., min_length=1)

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[Constraint]) -> list[Constraint]:
        """Validate constraints property

        :param v: Constraints property to validate
        :raises ValueError: If no ``DefiningContextConstraint`` with
            ``Relation.SEQUENCE_LIFTOVER`` in ``relations`` is found in ``constraints``
            or if neither ``CopyCountConstraint`` nor ``CopyChangeConstraint`` is found
            in ``constraints``.
        :return: Constraints property
        """
        defining_context_found = False
        copy_found = False

        for constraint in v:
            if not defining_context_found:
                defining_context_found = (
                    isinstance(constraint, DefiningContextConstraint)
                    and constraint.relations
                    and Relation.SEQUENCE_LIFTOVER in constraint.relations
                )

            if not copy_found:
                copy_found = isinstance(
                    constraint, CopyChangeConstraint | CopyCountConstraint
                )

        if not defining_context_found:
            err_msg = f"At least one item in `constraints` must be a `DefiningContextConstraint`` and contain ``{Relation.SEQUENCE_LIFTOVER}` in `relations`."
            raise ValueError(err_msg)

        if not copy_found:
            err_msg = "At least one item in `constraints` must be a `CopyCountConstraint` or a `CopyChangeConstraint`."
            raise ValueError(err_msg)

        return v


class CategoricalCnv(CategoricalCnvProperties, CategoricalVariant):
    """A representation of the constraints for matching knowledge about CNVs."""
