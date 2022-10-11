from typing import Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.profile import Profile
from tracardi.process_engine.action.v1.internal.entity.entity_config_protocol import EntityConfigProtocol


def get_referenced_profile(config: EntityConfigProtocol, profile: Profile) -> Optional[str]:
    return profile.id \
        if isinstance(profile, Profile) and config.reference_profile is True \
        else None


def convert_entity_id(config: EntityConfigProtocol, id: str, profile: Profile) -> str:
    referenced_profile = get_referenced_profile(config, profile)

    event_type = config.type.id if isinstance(config.type, NamedEntity) else config.type

    if referenced_profile:
        entity_id = "{}-{}-{}".format(event_type, id, referenced_profile)
    else:
        entity_id = "{}-{}".format(event_type, id)

    return entity_id
