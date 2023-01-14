from enum import Enum


class IndexesSearch(str, Enum):
    resource = "resource"
    session = "session"
    profile = "profile"
    event = "event"
    rule = "rule"
    segment = "segment"
    flow = "flow",
    log = "log"


class IndexesAutocomplete(str, Enum):
    session = "session"
    profile = "profile"
    event = "event"