"""Define Pydantic models for GA4GH categorical variation objects.

See the `CatVar page <https://www.ga4gh.org/product/categorical-variation-catvar/>`_ on
the GA4GH website for more information.
"""

from enum import Enum
from typing import ClassVar, Literal

from pydantic import ConfigDict, Field, RootModel

from ga4gh.cat_vrs.metadata import CatVRSMetadataMixin
from ga4gh.core.metadata import Maturity
from ga4gh.core.models import (
    BaseModelForbidExtra,
    ConceptMapping,
    Entity,
    MappableConcept,
    iriReference,
)
from ga4gh.vrs.models import (
    Allele,
    CopyChange,
    Location,
    Range,
    SequenceExpression,
    SequenceLocation,
    Terminus,
    Variation,
)


class DefiningAlleleConstraint(CatVRSMetadataMixin, BaseModelForbidExtra):
    """The defining allele and its associated relationships that are congruent with
    member variants.
    """

    _maturity: ClassVar[Maturity] = Maturity.TRIAL_USE

    type: Literal["DefiningAlleleConstraint"] = Field(
        default="DefiningAlleleConstraint",
        description="MUST be 'DefiningAlleleConstraint'",
    )
    allele: Allele | iriReference
    relations: list[MappableConcept] | None = Field(
        default=None,
        description="Defined relationships from which members relate to the defining allele.",
    )


class DefiningLocationConstraint(CatVRSMetadataMixin, BaseModelForbidExtra):
    """The defining location and its associated relationships that are congruent with
    member locations.
    """

    _maturity: ClassVar[Maturity] = Maturity.TRIAL_USE

    type: Literal["DefiningLocationConstraint"] = Field(
        default="DefiningLocationConstraint",
        description="MUST be 'DefiningLocationConstraint'",
    )
    location: SequenceLocation | iriReference
    relations: list[MappableConcept] | None = Field(
        default=None,
        description="Defined relationships from which members relate to the defining location.",
    )
    matchCharacteristic: MappableConcept = Field(
        ...,
        description="A characteristic of the location that is used to match the defining location to member locations.",
    )


class FunctionalDomainStatus(str, Enum):
    """Define whether a functional domain is preserved or lost."""

    LOST = "lost"
    PRESERVED = "preserved"


class FunctionalDomain(CatVRSMetadataMixin, Entity, BaseModelForbidExtra):
    """A sequence location whose presence or absence is used to define an adjacency."""

    model_config = ConfigDict(use_enum_values=True)

    _maturity: ClassVar[Maturity] = Maturity.DRAFT

    type: Literal["FunctionalDomain"] = Field(
        default="FunctionalDomain", description='Must be "FunctionalDomain"'
    )
    location: Location = Field(..., description="A Sequence Location for the domain.")
    status: FunctionalDomainStatus = Field(
        ..., description='MUST be either "preserved" or "lost"'
    )


class UnspecifiedElement(CatVRSMetadataMixin, Entity, BaseModelForbidExtra):
    """Represents an unspecified element that satisfies the described adjacency."""

    _maturity: ClassVar[Maturity] = Maturity.DRAFT

    type: Literal["UnspecifiedElement"] = Field(
        default="UnspecifiedElement", description='Must be "UnspecifiedElement"'
    )


class AdjacencyConstraint(CatVRSMetadataMixin, BaseModelForbidExtra):
    """Components that define a molecular adjacency of congruent elements."""

    _maturity: ClassVar[Maturity] = Maturity.DRAFT

    type: Literal["AdjacencyConstraint"] = Field(
        default="AdjacencyConstraint",
        description="MUST be 'AdjacencyConstraint'",
    )
    adjoinedElements: list[
        UnspecifiedElement | MappableConcept | iriReference | Location | Terminus
    ] = Field(
        ..., min_length=2, max_length=2, description="The elements of the adjacency."
    )
    functionalDomains: list[FunctionalDomain] | None = Field(
        default=None,
        description="Functional domains whose presence or absence is required to satisfy the adjacency.",
    )
    linker: SequenceExpression | None = Field(
        default=None, description="The sequence found between the adjoined elements."
    )
    orderKnown: bool = Field(
        ...,
        description="When orderKnown is true, the order of adjoinedElements is assumed to denote the 5' partner first and the 3' partner second. If orderKnown is false, then the order of adjoinedElements assumed not in fact to be known, as in the case of a fusion where only one or both partners are known, but not their relative order. This field is redundant and may be set to true when using Sequence Locations and following the VRS 2 Adjacency model, as the order is implied by the usage of start and end on respective adjoinedElements.",
    )


class CopyCountConstraint(CatVRSMetadataMixin, BaseModelForbidExtra):
    """The exact or range of copies that members of this categorical variant must
    satisfy.
    """

    _maturity: ClassVar[Maturity] = Maturity.TRIAL_USE

    type: Literal["CopyCountConstraint"] = Field(
        default="CopyCountConstraint", description="MUST be 'CopyCountConstraint'"
    )
    copies: int | Range = Field(
        ...,
        description="The precise value or range of copies members of this categorical variant must satisfy.",
    )


class CopyChangeConstraint(CatVRSMetadataMixin, BaseModelForbidExtra):
    """The relative assessment of the change in copies that members of this categorical
    variant satisfy.
    """

    _maturity: ClassVar[Maturity] = Maturity.DRAFT

    type: Literal["CopyChangeConstraint"] = Field(
        default="CopyChangeConstraint", description="MUST be 'CopyChangeConstraint'"
    )
    copyChange: CopyChange = Field(
        ...,
        description="The relative assessment of the change in copies that members of this categorical variant satisfies.",
    )


class FeatureContextConstraint(CatVRSMetadataMixin, BaseModelForbidExtra):
    """The feature that members of this categorical variant are associated with."""

    _maturity: ClassVar[Maturity] = Maturity.DRAFT

    type: Literal["FeatureContextConstraint"] = Field(
        default="FeatureContextConstraint",
        description="MUST be 'FeatureContextConstraint'",
    )
    featureContext: MappableConcept = Field(..., description="A feature identifier.")


class FunctionConstraint(CatVRSMetadataMixin, BaseModelForbidExtra):
    """A classification of the protein functional consequence that characterizes members of this categorical variant."""

    _maturity: ClassVar[Maturity] = Maturity.DRAFT

    type: Literal["FunctionConstraint"] = Field(
        default="FunctionConstraint",
        description='MUST be "FunctionConstraint"',
    )
    functionConsequence: MappableConcept = Field(
        ...,
        description="The functional consequence of members of this categorical variant, as defined by an external ontology. We recommend using one of the defined terms from [The Sequence Ontology](http://www.sequenceontology.org). See Implementation Guidance for more details. ",
    )
    description: str | None = Field(
        default=None, description="A free-text description of the function change."
    )


class Constraint(CatVRSMetadataMixin, RootModel):
    """Constraints are used to construct an intensional semantics of categorical variant types."""

    _maturity: ClassVar[Maturity] = Maturity.TRIAL_USE

    root: (
        DefiningAlleleConstraint
        | DefiningLocationConstraint
        | AdjacencyConstraint
        | FeatureContextConstraint
        | CopyCountConstraint
        | CopyChangeConstraint
        | FunctionConstraint
    ) = Field(..., discriminator="type")


class CategoricalVariant(CatVRSMetadataMixin, Entity, BaseModelForbidExtra):
    """A representation of a categorically-defined domain for variation, in which
    individual Constraintual variation instances may be members of the domain.
    """

    _maturity: ClassVar[Maturity] = Maturity.TRIAL_USE

    type: Literal["CategoricalVariant"] = Field(
        default="CategoricalVariant", description="MUST be 'CategoricalVariant'"
    )
    name: str = Field(..., description="A primary name for the entity.")
    members: list[Variation | iriReference] | None = Field(
        default=None,
        description="A non-exhaustive list of VRS Variations that satisfy the constraints of this categorical variant.",
    )
    constraints: list[Constraint] | None = None
    mappings: list[ConceptMapping] | None = Field(
        default=None,
        description="A list of mappings to concepts in terminologies or code systems. Each mapping should include a coding and a relation.",
    )
