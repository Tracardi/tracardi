from typing import Protocol, List


class HCacheProtocol(Protocol):
    def hexists(self, name, key):
        pass

    def hset(self, name, key, value):
        pass

    def hget(self, name, key):
        pass

    def hdel(self, name: str, *keys: List):
        pass
