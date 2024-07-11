"""Define Pydantic models for GA4GH categorical variation objects.

See the `CatVar page <https://www.ga4gh.org/product/categorical-variation-catvar/>`_ on
the GA4GH website for more information.
"""

from enum import Enum
from typing import Literal

from ga4gh.core.entity_models import IRI, _DomainEntity
from ga4gh.vrs.models import (
    Adjacency,
    Allele,
    CisPhasedBlock,
    CopyChange,
    CopyNumberChange,
    CopyNumberCount,
    DerivativeSequence,
    Range,
    SequenceLocation,
    SequenceTerminus,
)
from pydantic import BaseModel, Field, RootModel, StrictStr


class CatVrsType(str, Enum):
    """Define CatVRS types"""

    PROTEIN_SEQ_CONS = "ProteinSequenceConsequence"
    CANONICAL_ALLELE = "CanonicalAllele"
    CATEGORICAL_CNV = "CategoricalCnv"
    DESCRIBED_VAR = "DescribedVariation"
    NUMBER_COUNT = "NumberCount"
    NUMBER_CHANGE = "NumberChange"
    QUANTITY_VARIANCE = "QuantityVariance"


class LocationMatchCharacteristic(str, Enum):
    """The characteristics of a valid match between a contextual CNV location (the
    query) and the Categorical CNV location (the domain), when both query and domain are
    represented on the same reference sequence. An ``exact`` match requires the location
    of the query and domain to be identical. A ``subinterval`` match requires the query
    to be a subinterval of the domain. A ``superinterval`` match requires the query to
    be a superinterval of the domain. A ``partial`` match requires at least 1 residue of
    overlap between the query and domain.
    """

    EXACT = "exact"
    PARTIAL = "partial"
    SUBINTERVAL = "subinterval"
    SUPERINTERVAL = "superinterval"


class _CategoricalVariationBase(_DomainEntity):
    """Base class for Categorical Variation"""

    members: (
        list[
            Allele
            | CisPhasedBlock
            | Adjacency
            | SequenceTerminus
            | DerivativeSequence
            | CopyNumberChange
            | CopyNumberCount
            | IRI,
        ]
        | None
    ) = Field(
        None,
        description="A non-exhaustive list of VRS variation contexts that satisfy the constraints of this categorical variant.",
    )


class ProteinSequenceConsequence(_CategoricalVariationBase):
    """A change that occurs in a protein sequence as a result of genomic changes. Due to
    the degenerate nature of the genetic code, there are often several genomic changes
    that can cause a protein sequence consequence. The protein sequence consequence,
    like a ``CanonicalAllele``, is defined by an
    `Allele <https://vrs.ga4gh.org/en/2.0/terms_and_model.html#variation>`_ that is
    representative of a collection of congruent Protein Alleles that share the same
    altered codon(s).
    """

    type: Literal[CatVrsType.PROTEIN_SEQ_CONS] = Field(
        CatVrsType.PROTEIN_SEQ_CONS,
        description=f"MUST be '{CatVrsType.PROTEIN_SEQ_CONS.value}'.",
    )
    definingContext: Allele | IRI = Field(  # noqa: N815
        ...,
        description="The `VRS Allele <https://vrs.ga4gh.org/en/2.0/terms_and_model.html#allele>`_  object that is congruent with (projects to the same codons) as alleles on other protein reference sequences.",
    )


class CanonicalAllele(_CategoricalVariationBase):
    """A canonical allele is defined by an
    `Allele <https://vrs.ga4gh.org/en/2.0/terms_and_model.html#variation>`_ that is
    representative of a collection of congruent Alleles, each of which depict the same
    nucleic acid change on different underlying reference sequences. Congruent
    representations of an Allele often exist across different genome assemblies and
    associated cDNA transcript representations.
    """

    type: Literal[CatVrsType.CANONICAL_ALLELE] = Field(
        CatVrsType.CANONICAL_ALLELE,
        description=f"MUST be '{CatVrsType.CANONICAL_ALLELE.value}'.",
    )
    definingContext: Allele | IRI = Field(  # noqa: N815
        ...,
        description="The `VRS Allele <https://vrs.ga4gh.org/en/2.0/terms_and_model.html#allele>`_ object that is congruent with variants on alternate reference sequences.",
    )


class CategoricalCnv(_CategoricalVariationBase):
    """A categorical variation domain is defined first by a sequence derived from a
    canonical `Location <https://vrs.ga4gh.org/en/2.0/terms_and_model.html#Location>`_ ,
    which is representative of a collection of congruent Locations. The change or count
    of this sequence is also described, either by a numeric value (e.g. "3 or more
    copies") or categorical representation (e.g. "high-level gain"). Categorical CNVs
    may optionally be defined by rules specifying the location match characteristics for
    member CNVs.
    """

    type: Literal[CatVrsType.CATEGORICAL_CNV] = Field(
        CatVrsType.CATEGORICAL_CNV,
        description=f"MUST be '{CatVrsType.CATEGORICAL_CNV.value}'.",
    )
    location: SequenceLocation = Field(
        ...,
        description="A `VRS Location <https://vrs.ga4gh.org/en/2.0/terms_and_model.html#location>`_ object that represents a sequence derived from that location, and is congruent with locations on alternate reference sequences.",
    )
    locationMatchCharacteristic: LocationMatchCharacteristic | None = Field(  # noqa: N815
        None,
        description="The characteristics of a valid match between a contextual CNV location (the query) and the Categorical CNV location (the domain), when both query and domain are represented on the same reference sequence. An `exact` match requires the location of the query and domain to be identical. A `subinterval` match requires the query to be a subinterval of the domain. A `superinterval` match requires the query to be a superinterval of the domain. A `partial` match requires at least 1 residue of overlap between the query and domain.",
    )
    copyChange: CopyChange | None = Field(  # noqa: N815
        None,
        description="A representation of the change in copies of a sequence in a system. MUST be one of 'efo:0030069' (complete genomic loss), 'efo:0020073' (high-level loss), 'efo:0030068' (low-level loss), 'efo:0030067' (loss), 'efo:0030064' (regional base ploidy), 'efo:0030070' (gain), 'efo:0030071' (low-level gain), 'efo:0030072' (high-level gain).",
    )
    copies: int | Range | None = Field(
        None, description="The integral number of copies of the subject in a system."
    )


class DescribedVariation(_CategoricalVariationBase):
    """Some categorical variation concepts are supported by custom nomenclatures or
    text-descriptive representations for which a categorical variation model does not
    exist. DescribedVariation is a class that adds requirements and contextual semantics
    to the ``label`` and ``description`` fields to indicate how a categorical variation
    concept should be evaluated for matching variants.
    """

    type: Literal[CatVrsType.DESCRIBED_VAR] = Field(
        CatVrsType.DESCRIBED_VAR,
        description=f"MUST be '{CatVrsType.DESCRIBED_VAR.value}'.",
    )
    label: StrictStr = Field(
        ...,
        description="A primary label for the categorical variation. This required property should provide a short and descriptive textual representation of the concept.",
    )
    description: StrictStr | None = Field(
        None,
        description="A textual description of the domain of variation that should match the categorical variation entity.",
    )


class CategoricalVariation(RootModel):
    """A representation of a categorically-defined domain for variation, in which
    individual contextual variation instances may be members of the domain.
    """

    root: (
        CanonicalAllele
        | CategoricalCnv
        | DescribedVariation
        | ProteinSequenceConsequence
    ) = Field(
        ...,
        json_schema_extra={
            "description": "A representation of a categorically-defined domain for variation, in which individual contextual variation instances may be members of the domain.",
        },
        discriminator="type",
    )


class NumberCount(BaseModel):
    """The absolute count of a discrete assayable unit (e.g. chromosome, gene, or sequence)."""

    type: Literal[CatVrsType.NUMBER_COUNT] = Field(
        CatVrsType.NUMBER_COUNT, description=f"MUST be '{CatVrsType.NUMBER_COUNT}'."
    )
    count: int | Range = Field(
        ...,
        description="The integral quantity or quantity range of the subject in a system",
    )


class NumberChange(BaseModel):
    """A quantitative assessment of a unit within a system (e.g. genome, cell, etc.)
    relative to a baseline quantity.
    """

    type: Literal[CatVrsType.NUMBER_CHANGE] = Field(
        CatVrsType.NUMBER_CHANGE, description=f"MUST be '{CatVrsType.NUMBER_CHANGE}'."
    )
    change: int | Range | CopyChange = Field(
        ...,
        description="a quantitative or qualitative value of the measurement with respect to a baseline (0). If qualitative, must be one of 'efo:0030069' (complete genomic loss), 'efo:0020073' (high-level loss), 'efo:0030068' (low-level loss), 'efo:0030067' (loss), 'efo:0030064' (regional base ploidy), 'efo:0030070' (gain), 'efo:0030071' (low-level gain), 'efo:0030072' (high-level gain).",
    )


class QuantityVariance(BaseModel):
    """The Quantity Variance class captures one axis of variation in the generalized
    model of categorical variation.  It is used to model quantitative measure changes in
    a given biological level of variation.
    """

    type: Literal[CatVrsType.QUANTITY_VARIANCE] = Field(
        CatVrsType.QUANTITY_VARIANCE,
        description=f"MUST be '{CatVrsType.QUANTITY_VARIANCE}'.",
    )


class CategoricalVariant(_DomainEntity):
    """A top-level representation of a categorically-defined domain for variation across
    one or multiple biological levels in which individual contextual variants may be
    members of the domain.
    """
