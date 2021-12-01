from typing import Protocol


class Debuggable(Protocol):
    debug: bool
