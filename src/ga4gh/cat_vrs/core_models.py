"""Define Pydantic models for GA4GH categorical variation objects.

See the `CatVar page <https://www.ga4gh.org/product/categorical-variation-catvar/>`_ on
the GA4GH website for more information.
"""

from enum import Enum
from typing import Literal

from ga4gh.core.entity_models import IRI, Coding, DomainEntity
from ga4gh.vrs.models import CopyChange, Location, Range, Variation
from pydantic import BaseModel, Field, RootModel, field_validator


class Relation(str, Enum):
    """Defined relationships between members of the categorical variant and the defining
    context. ``sequence_liftover`` refers to variants or locations that represent a
    congruent concept on a differing assembly of a human genome (e.g. "GRCh37" and
    "GRCh38") or gene (e.g. Locus Reference Genomic) sequence. ``transcript_projection``
    refers to variants or locations that occur on transcripts projected from the defined
    genomic concept. ``codon_translation`` refers to variants or locations that
    translate from the codon(s) represented by the defined concept.
    """

    SEQUENCE_LIFTOVER = "sequence_liftover"
    TRANSCRIPT_PROJECTION = "transcript_projection"
    CODON_TRANSLATION = "codon_translation"


class DefiningContextConstraint(BaseModel):
    """The location or location-state, congruent with other reference sequences, about
    which categorical variation is being described.
    """

    type: Literal["DefiningContextConstraint"] = Field(
        "DefiningContextConstraint", description="MUST be 'DefiningContextConstraint'"
    )
    definingContext: Variation | Location | IRI  # noqa: N815
    relations: list[Relation] | None = Field(
        None,
        description="Defined relationships between members of the categorical variant and the defining context. ``sequence_liftover`` refers to variants or locations that represent a congruent concept on a differing assembly of a human genome (e.g. 'GRCh37' and 'GRCh38') or gene (e.g. Locus Reference Genomic) sequence. ``transcript_projection`` refers to variants or locations that occur on transcripts projected from the defined genomic concept. ``codon_translation`` refers to variants or locations that translate from the codon(s) represented by the defined concept.",
    )


class CopyCountConstraint(BaseModel):
    """The absolute number of copies in a system"""

    type: Literal["CopyCountConstraint"] = Field(
        "CopyCountConstraint", description="MUST be 'CopyCountConstraint'"
    )
    copies: int | Range


class CopyChangeConstraint(BaseModel):
    """A representation of copy number change"""

    type: Literal["CopyChangeConstraint"] = Field(
        "CopyChangeConstraint", description="MUST be 'CopyChangeConstraint'"
    )
    copyChange: Coding  # noqa: N815

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

    root: DefiningContextConstraint | CopyCountConstraint | CopyChangeConstraint = (
        Field(..., discriminator="type")
    )


class CategoricalVariant(DomainEntity):
    """A representation of a categorically-defined domain for variation, in which
    individual contextual variation instances may be members of the domain.
    """

    type: Literal["CategoricalVariant"] = Field(
        "CategoricalVariant", description="MUST be 'CategoricalVariant'"
    )
    members: list[Variation | IRI] | None = Field(
        None,
        description="A non-exhaustive list of VRS variation contexts that satisfy the constraints of this categorical variant.",
    )
    constraints: list[Constraint] | None = None
