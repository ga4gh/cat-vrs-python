"""Define Pydantic models for GA4GH categorical variation objects.

See the `CatVar page <https://www.ga4gh.org/product/categorical-variation-catvar/>`_ on
the GA4GH website for more information.
"""

from pydantic import Field, field_validator

from ga4gh.cat_vrs.models import (
    CategoricalVariant,
    Constraint,
    CopyChangeConstraint,
    CopyCountConstraint,
    DefiningAlleleConstraint,
    DefiningLocationConstraint,
)
from ga4gh.cat_vrs.relations import (
    LIFTOVER_TO_RELATION,
    TRANSCRIBED_TO_RELATION,
    TRANSLATION_OF_RELATION,
)
from ga4gh.core.models import MappableConcept


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

    @classmethod
    def required_relations(cls) -> list[MappableConcept]:
        """Return relations required for defining allele constraints."""
        return [TRANSLATION_OF_RELATION]

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[Constraint]) -> list[Constraint]:
        """Validate constraints property

        At least one constraint in ``constraints`` must satisfy ALL of the following
        requirements:
        1. Must be a ``DefiningAlleleConstraint``
        2. Must have ``relations`` property that meets ALL of the following
        requirements:
            a. Must contain exactly one ``TRANSLATION_OF_RELATION``

        :param v: Constraints property to validate
        :raises ValueError: If constraints property does not satisfy the requirements
        :return: Constraints property
        """
        required_relations = cls.required_relations()
        required_relation = required_relations[0]
        if not any(
            isinstance(constraint.root, DefiningAlleleConstraint)
            and constraint.root.relations
            and sum(1 for r in constraint.root.relations if r in required_relations)
            == 1
            for constraint in v
        ):
            err_msg = f"Unable to find at least one constraint that is a `DefiningAlleleConstraint` and has exactly one `relation` where the `primaryCoding.code` is '{required_relation.primaryCoding.code.root}' and `primaryCoding.system` is '{required_relation.primaryCoding.system}'."
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

    @classmethod
    def required_relations(cls) -> list[MappableConcept]:
        """Return relations required for canonical allele constraints."""
        return [LIFTOVER_TO_RELATION, TRANSCRIBED_TO_RELATION]

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[Constraint]) -> list[Constraint]:
        """Validate constraints property

        Exactly one constraint in ``constraints`` must satisfy ALL of the following
        requirements:
        1. Must be a ``DefiningAlleleConstraint``
        2. Must have ``relations`` property that meets ALL of the following
        requirements:
            a. Must contain exactly one ``LIFTOVER_TO_RELATION``
            b. Must contain exactly one ``TRANSCRIBED_TO_RELATION``

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

        for required_relation in cls.required_relations():
            if sum(1 for r in constraint.root.relations if r == required_relation) != 1:
                err_msg = f"Must contain exactly one relation where `primaryCoding.code` is '{required_relation.primaryCoding.code.root}' and `primaryCoding.system` is '{required_relation.primaryCoding.system}'."
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
                at least one ``LIFTOVER_TO_RELATION``
            2. Either a ``CopyCountConstraint`` or ``CopyChangeCount``

        :param v: Constraints property to validate
        :raises ValueError: If constraints property does not satisfy the requirements
        :return: Constraints property
        """
        defining_location = None
        copy_constraint_found = False

        for constraint_ in v:
            constraint = constraint_.root

            if isinstance(constraint, DefiningLocationConstraint):
                defining_location = constraint
                continue

            if isinstance(constraint, CopyCountConstraint | CopyChangeConstraint):
                copy_constraint_found = True

        liftover_relation_missing_msg = f"at least one relation where `primaryCoding.code` is '{LIFTOVER_TO_RELATION.primaryCoding.code.root}' and `primaryCoding.system` is '{LIFTOVER_TO_RELATION.primaryCoding.system}'."

        if not defining_location:
            err_msg = f"Must contain a `DefiningLocationConstraint` with {liftover_relation_missing_msg}."
            raise ValueError(err_msg)

        relations = defining_location.relations or []
        if not any(r == LIFTOVER_TO_RELATION for r in relations):
            err_msg = f"`DefiningLocationConstraint` found, but must contain {liftover_relation_missing_msg}"
            raise ValueError(err_msg)

        if not copy_constraint_found:
            err_msg = (
                "Must contain either a `CopyCountConstraint` or `CopyChangeConstraint`."
            )
            raise ValueError(err_msg)

        return v
