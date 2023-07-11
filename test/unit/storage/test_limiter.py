from time import sleep
from uuid import uuid4

from tracardi.context import ServerContext, Context
from tracardi.service.throttle import Limiter


def test_should_limit_calls():
    with ServerContext(Context(production=False)):
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

