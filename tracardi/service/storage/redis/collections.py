from dataclasses import dataclass


@dataclass
class Queue:
    segmentation: str = "segmentation:live"
    copy: str = "event_to_profile_coping:worker"
    event_props_to_event_traits: str = "event_props_to_event_traits:worker"


@dataclass
class Collection:
    throttle: str = "throttle:"  # Cache for limiter plugin
    token: str = "token:"  # Cache for token memory/db for authentication
    plugin_memory: str = "plugin-memory:"  # HASH
    profile_copy: str = "profile-copy:"  # HASH
    profile: str = "profile:"  # HASH
    session: str = "session:"  # HASH
    lock: str = "lock:"  # HASH
    session_lock: str = "session:lock:"  # HASH
    profile_fields: str = "profile:fields"  # SET, Cache profile fields, properties for auto completion
    event_fields: str = "event:fields"  # SET, Cache event fields, properties for auto completion
    session_fields: str = "session:fields"  # Cache session fields, properties for auto completion
    postpone_schedule: str = "delay:schedule-flag"  # Cache postponed execution (call)
    postpone_flag: str = "delay:postpone-flag"  # Cache postponed execution (call)
    exec_instance: str = "delay:exec-instance"  # Cache postponed execution (call)
    value_threshold: str = "value-threshold:"  # Cache for WF value threshold
    browser_finger_print: str = 'profile:finger:browser'  # Cache for profile by browser fingerprint
