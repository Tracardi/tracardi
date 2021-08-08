from enum import Enum


class IndexesSearch(str, Enum):
    source = "source"
    session = "session"
    profile = "profile"
    event = "event"
    rule = "rule"
    segment = "segment"
    flow = "flow"
