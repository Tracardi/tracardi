from enum import Enum


class IndexesHistogram(str, Enum):
    session = "session"
    profile = "profile"
    event = "event"
