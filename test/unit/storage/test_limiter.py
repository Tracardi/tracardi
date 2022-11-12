from time import sleep
from uuid import uuid4

from tracardi.service.throttle import Limiter


def test_should_limit_calls():
    limit = 3
    limiter = Limiter(limit=limit, ttl=10)
    key = str(uuid4())
    passes = 0
    while True:
        passes += 1
        block, ttl = limiter.limit(key)

        if block is False:
            break

        sleep(0.5)

    assert passes == limit

