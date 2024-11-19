from typing import Protocol


class MemberCacheProtocol(Protocol):
    def smembers(self, name):
        pass

    def sadd(self, name: str, *values):
        pass