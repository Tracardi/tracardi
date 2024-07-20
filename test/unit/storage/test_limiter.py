from time import sleep
from uuid import uuid4

from tracardi.context import ServerContext, Context
from tracardi.service.throttle import Limiter
from unittest.mock import patch


class MockRedis:

    def __init__(self):
        self.data = {}
        self._ttl = {}

    def incr(self, key):
        if key not in self.data:
            self.data[key] = 0
        self.data[key] += 1
        return self.data[key]

    def expire(self, key, ttl):
        self._ttl[key] = ttl

    def ttl(self, key):
        if key not in self._ttl:
            return 0
        return self._ttl[key]


def test_should_limit_calls():
    with ServerContext(Context(production=False)):

        with patch("tracardi.service.throttle.RedisClient",
                   return_value=MockRedis()) as mock_redis_client:

            limit = 3
            limiter = Limiter(limit=limit, ttl=10)
            key = str(uuid4())
            passes = 0
            while True:
                block, ttl = limiter.limit(key)

                if block is False:
                    break
                passes += 1
                sleep(0.5)

            assert passes == limit
