"""Define Pydantic models for GA4GH categorical variation objects.

See the `CatVar page <https://www.ga4gh.org/product/categorical-variation-catvar/>`_ on
the GA4GH website for more information.
"""

from enum import Enum

from ga4gh.cat_vrs.models import (
    CategoricalVariant,
    Constraint,
    CopyChangeConstraint,
    CopyCountConstraint,
    DefiningAlleleConstraint,
    DefiningLocationConstraint,
    Relation,
)
from pydantic import Field, field_validator


class SystemUri(str, Enum):
    """Define constraints for systems"""

    SEQUENCE_ONTOLOGY = "http://www.sequenceontology.org"
    GKS_ALLELE_RELATION = "ga4gh-gks-term:allele-relation"


class ProteinSequenceConsequence(CategoricalVariant):
    """A change that occurs in a protein sequence as a result of genomic changes. Due to
    the degenerate nature of the genetic code, there are often several genomic changes
    that can cause a protein sequence consequence. The protein sequence consequence,
    like a :ref:`CanonicalAllele`, is defined by an
    `Allele <https://vrs.ga4gh.org/en/2.x/concepts/MolecularVariation/Allele.html#>`_
    that is representative of a collection of congruent Protein Alleles that share the
    same altered codon(s).
    """

    constraints: list[Constraint] = Field(..., min_length=1)

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[Constraint]) -> list[Constraint]:
        """Validate constraints property

        At least one constraint in ``constraints`` must satisfy ALL of the following
        requirements:
        1. Must be a ``DefiningAlleleConstraint``
        2. Must have ``relations`` property that meets ALL of the following
        requirements:
            a. Must contain exactly one relation where ``primaryCoding.code = translation_of``
               and ``primaryCoding.system = http://www.sequenceontology.org``

        :param v: Constraints property to validate
        :raises ValueError: If constraints property does not satisfy the requirements
        :return: Constraints property
        """
        if not any(
            isinstance(constraint.root, DefiningAlleleConstraint)
            and constraint.root.relations
            and sum(
                1
                for r in constraint.root.relations
                if r.primaryCoding
                and r.primaryCoding.code.root == Relation.TRANSLATION_OF.value
                and r.primaryCoding.system == SystemUri.SEQUENCE_ONTOLOGY.value
            )
            == 1
            for constraint in v
        ):
            err_msg = f"Unable to find at least one constraint that is a `DefiningAlleleConstraint` and has exactly one `relation` where the `primaryCoding.code` is '{Relation.TRANSLATION_OF.value}' and `primaryCoding.system` is '{SystemUri.SEQUENCE_ONTOLOGY.value}'."
            raise ValueError(err_msg)

        return v


class CanonicalAllele(CategoricalVariant):
    """A canonical allele is defined by an
    `Allele <https://vrs.ga4gh.org/en/2.x/concepts/MolecularVariation/Allele.html#>`_
    that is representative of a collection of congruent Alleles, each of which depict
    the same nucleic acid change on different underlying reference sequences. Congruent
    representations of an Allele often exist across different genome assemblies and
    associated cDNA transcript representations.
    """

    constraints: list[Constraint] = Field(..., min_length=1, max_length=1)

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[Constraint]) -> list[Constraint]:
        """Validate constraints property

        Exactly one constraint in ``constraints`` must satisfy ALL of the following
        requirements:
        1. Must be a ``DefiningAlleleConstraint``
        2. Must have ``relations`` property that meets ALL of the following
        requirements:
            a. Must contain exactly one relation where ``primaryCoding.code = liftover_to`` and ``primaryCoding.system == ga4gh-gks-term:allele-relation``
            b. Must contain exactly one relation where ``primaryCoding.code = transcribed_to`` and ``primaryCoding.system == http://www.sequenceontology.org``

        :param v: Constraints property to validate
        :raises ValueError: If constraints property does not satisfy the requirements
        :return: Constraints property
        """
        constraint = v[0]

        if not isinstance(constraint.root, DefiningAlleleConstraint):
            err_msg = "Constraint must be a `DefiningAlleleConstraint`."
            raise ValueError(err_msg)

        if not constraint.root.relations:
            err_msg = "`relations` is required."
            raise ValueError(err_msg)

        if (
            sum(
                1
                for r in constraint.root.relations
                if r.primaryCoding
                and (
                    r.primaryCoding.code.root == Relation.LIFTOVER_TO.value
                    and r.primaryCoding.system == SystemUri.GKS_ALLELE_RELATION.value
                )
            )
            != 1
        ):
            err_msg = f"Must contain exactly one relation where `primaryCoding.code` is '{Relation.LIFTOVER_TO.value}' and `primaryCoding.system` is '{SystemUri.GKS_ALLELE_RELATION.value}'."
            raise ValueError(err_msg)

        if (
            sum(
                1
                for r in constraint.root.relations
                if r.primaryCoding
                and (
                    r.primaryCoding.code.root == Relation.TRANSCRIBED_TO.value
                    and r.primaryCoding.system == SystemUri.SEQUENCE_ONTOLOGY.value
                )
            )
            != 1
        ):
            err_msg = f"Must contain exactly one relation where `primaryCoding.code` is '{Relation.TRANSCRIBED_TO.value}' and `primaryCoding.system` is '{SystemUri.SEQUENCE_ONTOLOGY.value}'."
            raise ValueError(err_msg)

        return v


class CategoricalCnv(CategoricalVariant):
    """A representation of the constraints for matching knowledge about CNVs."""

    constraints: list[Constraint] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="The constraints array must contain exactly two items: a DefiningLocationConstraint and either a CopyChangeConstraint or CopyCountConstraint.",
    )

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[Constraint]) -> list[Constraint]:
        """Validate constraints property

        ``constraints`` must contain two constraints:
            1. ``DefiningLocationConstraint`` where the ``relations`` property contains
                at least one relation where ``primaryCoding.code = liftover_to`` and ``primaryCoding.system = ga4gh-gks-term:allele-relation``
            2. Either a ``CopyCountConstraint`` or ``CopyChangeCount``

        :param v: Constraints property to validate
        :raises ValueError: If constraints property does not satisfy the requirements
        :return: Constraints property
        """
        def_loc_constr_found = False
        def_loc_constr_valid = False
        copy_constr_found = False

        for constraint in v:
            constraint = constraint.root
            if not def_loc_constr_valid and isinstance(
                constraint, DefiningLocationConstraint
            ):
                def_loc_constr_found = True

                for r in constraint.relations:
                    if r.primaryCoding and (
                        r.primaryCoding.code.root == Relation.LIFTOVER_TO.value
                        and r.primaryCoding.system
                        == SystemUri.GKS_ALLELE_RELATION.value
                    ):
                        def_loc_constr_valid = True
                        continue

            if not copy_constr_found:
                copy_constr_found = isinstance(
                    constraint, CopyCountConstraint | CopyChangeConstraint
                )

        if not def_loc_constr_found:
            err_msg = f"Must contain a `DefiningLocationConstraint` with at least one relation where `primaryCoding.code` is '{Relation.LIFTOVER_TO.value}' and `primaryCoding.system` is '{SystemUri.GKS_ALLELE_RELATION.value}'."
            raise ValueError(err_msg)

        if not def_loc_constr_valid:
            err_msg = f"`DefiningLocationConstraint` found, but must contain at least one relation where `primaryCoding.code` is '{Relation.LIFTOVER_TO.value}' and `primaryCoding.system` is '{SystemUri.GKS_ALLELE_RELATION.value}'."
            raise ValueError(err_msg)

        if not copy_constr_found:
            err_msg = (
                "Must contain either a `CopyCountConstraint` or `CopyChangeConstraint`."
            )
            raise ValueError(err_msg)

        return v
