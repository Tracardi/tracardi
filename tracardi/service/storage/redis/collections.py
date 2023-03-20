from dataclasses import dataclass


@dataclass
class Queue:
    segmentation: str = "segmentation:live"
    copy: str = "event_to_profile_coping:worker"


@dataclass
class Collection:
    throttle: str = "throttle:"
    token: str = "token:"
    plugin_memory: str = "plugin-memory:"
    profile: str = "profile:"
