from typing import Protocol, Union

from tracardi.domain.named_entity import NamedEntity


class EntityConfigProtocol(Protocol):
    id: str
    type: Union[NamedEntity, str]
    reference_profile: bool = True
