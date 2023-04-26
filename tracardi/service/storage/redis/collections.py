from dataclasses import dataclass


@dataclass
class Queue:
    segmentation: str = "segmentation:live"
    copy: str = "event_to_profile_coping:worker"
    event_props_to_event_traits: str = "event_props_to_event_traits:worker"


@dataclass
class Collection:
    throttle: str = "throttle:"
    token: str = "token:"
    plugin_memory: str = "plugin-memory:"
    profile: str = "profile:"
    profile_fields: str = "profile:fields"
    event_fields: str = "event:fields"
    session_fields: str = "session:fields"
