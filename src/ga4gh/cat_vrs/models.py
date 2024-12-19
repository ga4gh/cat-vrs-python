"""Define Pydantic models for GA4GH categorical variation objects.

See the `CatVar page <https://www.ga4gh.org/product/categorical-variation-catvar/>`_ on
the GA4GH website for more information.
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, RootModel, field_validator

from ga4gh.core.models import (
    Coding,
    ConceptMapping,
    Entity,
    MappableConcept,
    iriReference,
)
from ga4gh.vrs.models import Allele, CopyChange, Range, SequenceLocation, Variation


class Relation(str, Enum):
    """Defined relationships between members of the categorical variant and the defining
    context.
    """

    TRANSLATES_FROM = "translates_from"
    LIFTOVER_TO = "liftover_to"
    TRANSCRIBES_TO = "transcribes_to"


class DefiningAlleleConstraint(BaseModel):
    """The defining allele and its associated relationships that are congruent with
    member variants.
    """

    type: Literal["DefiningAlleleConstraint"] = Field(
        "DefiningAlleleConstraint", description="MUST be 'DefiningAlleleConstraint'"
    )
    allele: Allele | iriReference
    relations: list[MappableConcept] | None = Field(
        None,
        description="Defined relationships from which members relate to the defining allele.",
    )


class DefiningLocationConstraint(BaseModel):
    """The defining location and its associated relationships that are congruent with
    member locations.
    """

    type: Literal["DefiningLocationConstraint"] = Field(
        "DefiningLocationConstraint", description="MUST be 'DefiningLocationConstraint'"
    )
    location: SequenceLocation | iriReference
    relations: list[MappableConcept] | None = Field(
        None,
        description="Defined relationships from which members relate to the defining location.",
    )
    matchCharacteristic: MappableConcept = Field(
        ...,
        description="A characteristic of the location that is used to match the defining location to member locations.",
    )


class CopyCountConstraint(BaseModel):
    """The exact or range of copies that members of this categorical variant must
    satisfy.
    """

    type: Literal["CopyCountConstraint"] = Field(
        "CopyCountConstraint", description="MUST be 'CopyCountConstraint'"
    )
    copies: int | Range = Field(
        ...,
        description="The precise value or range of copies members of this categorical variant must satisfy.",
    )


class CopyChangeConstraint(BaseModel):
    """A representation of copy number change"""

    type: Literal["CopyChangeConstraint"] = Field(
        "CopyChangeConstraint", description="MUST be 'CopyChangeConstraint'"
    )
    copyChange: Coding = Field(
        ...,
        description="The relative assessment of the change in copies that members of this categorical variant satisfies.",
    )

    @field_validator("copyChange")
    @classmethod
    def validate_copy_change(cls, v: Coding) -> Coding:
        """Validate copyChange property

        :param v: copyChange value
        :raises ValueError: If ``copyChange.code`` is not a valid CopyChange
        :return: copyChange property
        """
        try:
            CopyChange(v.code.root)
        except ValueError as e:
            err_msg = f"copyChange, {v.code.root}, not one of {[cc.value for cc in CopyChange]}"
            raise ValueError(err_msg) from e
        return v


class Constraint(RootModel):
    """Constraints are used to construct an intensional semantics of categorical variant types."""

    root: (
        DefiningAlleleConstraint
        | DefiningLocationConstraint
        | CopyCountConstraint
        | CopyChangeConstraint
    ) = Field(..., discriminator="type")


class CategoricalVariant(Entity):
    """A representation of a categorically-defined domain for variation, in which
    individual Constraintual variation instances may be members of the domain.
    """

    type: Literal["CategoricalVariant"] = Field(
        "CategoricalVariant", description="MUST be 'CategoricalVariant'"
    )
    members: list[Variation | iriReference] | None = Field(
        None,
        description="A non-exhaustive list of VRS variation Constraints that satisfy the constraints of this categorical variant.",
    )
    constraints: list[Constraint] | None = None
    mappings: list[ConceptMapping] | None = Field(
        None,
        description="A list of mappings to concepts in terminologies or code systems. Each mapping should include a coding and a relation.",
    )
