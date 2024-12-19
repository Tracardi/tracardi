from typing import Protocol


class CacheProtocol(Protocol):

    def get(self, key: str):
        pass

    def set(self, key, value, ex=None, nx:bool=None):
        pass

    def mset(self, mapping):
        pass

    def delete(self, key, skip_tenant: bool = False):
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

    def set_msgpack(self, key, value, ex=None):
        pass

    def get_msgpack(self, key: str):
        pass

    def scan(self, match=None, count=None):
        pass