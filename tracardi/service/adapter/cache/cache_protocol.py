from typing import Protocol


class CacheProtocol(Protocol):

    def get(self, key: str):
        pass

    def set(self, key, value, ex):
        pass

    def mset(self, mapping):
        pass

    def delete(self, key):
        pass

    def exists(self, key: str):
        pass

    def expire(self, key, ttl):
        pass

    def incr(self, key: str):
        pass

    def ttl(self, key: str):
        pass

    def persist(self, key: str):
        pass

    def ping(self):
        pass