from enum import Enum


class TimeSpan(str, Enum):
    d = "d"
    w = "w"
    m = 'M'
    y = "y"
