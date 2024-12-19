"""Define Pydantic models for GA4GH categorical variation objects.

See the `CatVar page <https://www.ga4gh.org/product/categorical-variation-catvar/>`_ on
the GA4GH website for more information.
"""

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
            a. Must contain exactly one relation where ``primaryCode = translates_from``

        :param v: Constraints property to validate
        :raises ValueError: If constraints property does not satisfy the requirements
        :return: Constraints property
        """
        if not any(
            all(
                (
                    isinstance(constraint, DefiningAlleleConstraint),
                    constraint.relations,
                    sum(
                        1
                        for r in constraint.relations
                        if r.primaryCode == Relation.TRANSLATES_FROM
                    )
                    == 1,
                )
            )
            for constraint in v
        ):
            err_msg = f"Unable to find at least one constraint that is a `DefiningAlleleConstraint` and has exactly one `relation` where the `primaryCode` is '{Relation.TRANSLATES_FROM.value}'."
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
            a. Must contain exactly one relation where ``primaryCode = liftover_to``
            b. Must contain exactly one relation where ``primaryCode = transcribes_to``

        :param v: Constraints property to validate
        :raises ValueError: If constraints property does not satisfy the requirements
        :return: Constraints property
        """
        constraint = v[0]

        if not isinstance(constraint, DefiningAlleleConstraint):
            err_msg = "Constraint must be a `DefiningAlleleConstraint`."
            raise ValueError(err_msg)

        if not constraint.relations:
            err_msg = "`relations` is required."
            raise ValueError(err_msg)

        if (
            sum(
                1 for r in constraint.relations if r.primaryCode == Relation.LIFTOVER_TO
            )
            != 1
        ):
            err_msg = f"Must contain exactly one relation where `primaryCode` is '{Relation.LIFTOVER_TO.value}'."
            raise ValueError(err_msg)

        if (
            sum(
                1
                for r in constraint.relations
                if r.primaryCode == Relation.TRANSCRIBES_TO
            )
            != 1
        ):
            err_msg = f"Must contain exactly one relation where `primaryCode` is '{Relation.TRANSCRIBES_TO.value}."
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

        Each constraint in ``constraints`` must satisfy ALL of the following
        requirements:
        1. Must contain a ``DefiningLocationConstraint`` where
            a. ``relations`` property contains at least one relation where ``primaryCode = liftover_to``
        2. Must contain a ``CopyCountConstraint`` or ``CopyChangeConstraint``

        :param v: Constraints property to validate
        :raises ValueError: If constraints property does not satisfy the requirements
        :return: Constraints property
        """
        def_loc_constr_found = False
        copy_constr_found = False

        for constraint in v:
            if not def_loc_constr_found:
                def_loc_constr_found = (
                    isinstance(constraint, DefiningLocationConstraint)
                    and constraint.relations
                    and Relation.LIFTOVER_TO in constraint.relations
                )

            if not copy_constr_found:
                copy_constr_found = isinstance(
                    constraint, CopyCountConstraint | CopyChangeConstraint
                )

        if not def_loc_constr_found:
            err_msg = f"Must contain a `DefiningLocationConstraint` with at least one relation where `primaryCode` is {Relation.LIFTOVER_TO.value}."
            raise ValueError(err_msg)

        if not copy_constr_found:
            err_msg = (
                "Must contain either a `CopyCountConstraint` or `CopyChangeConstraint`."
            )
            raise ValueError(err_msg)

        return v
