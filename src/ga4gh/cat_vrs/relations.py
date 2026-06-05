"""Define enums and constants for relations."""

from enum import Enum

from ga4gh.core.models import Coding, MappableConcept, code


class Relation(str, Enum):
    """Defined relationships between members of the categorical variant and the defining
    context.
    """

    TRANSLATION_OF = "translation_of"
    LIFTOVER_TO = "liftover_to"
    TRANSCRIBED_TO = "transcribed_to"


class SystemUri(str, Enum):
    """Define constraints for systems used in relations"""

    SEQUENCE_ONTOLOGY = "http://www.sequenceontology.org"
    GKS_ALLELE_RELATION = "ga4gh-gks-term:allele-relation"


def _build_relation_concept(relation: Relation, system: SystemUri) -> MappableConcept:
    """Create a relation concept

    :param relation: Relation enum to describe the relationship
    :param system: The system that defines the relation
    :return: Mappable Concept representing the relation
    """
    return MappableConcept(
        primaryCoding=Coding(
            code=code(relation.value),
            system=system.value,
        )
    )


TRANSLATION_OF_RELATION = _build_relation_concept(
    Relation.TRANSLATION_OF, SystemUri.SEQUENCE_ONTOLOGY
)
LIFTOVER_TO_RELATION = _build_relation_concept(
    Relation.LIFTOVER_TO, SystemUri.GKS_ALLELE_RELATION
)
TRANSCRIBED_TO_RELATION = _build_relation_concept(
    Relation.TRANSCRIBED_TO, SystemUri.SEQUENCE_ONTOLOGY
)
