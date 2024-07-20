from time import sleep

from tracardi.context import ServerContext, Context
from tracardi.service.storage.redis.driver.redis_client import RedisClient
from tracardi.service.tracking.locking import Lock, RELEASED


def test_lock_ttl():
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock = Lock(redis, key, default_lock_ttl=1)
        assert lock.is_locked() is False
        lock.lock("name1")
        assert lock.is_locked() is True
        sleep(2)
        assert lock.is_locked() is False
        lock.unlock()

def test_lock_expires():
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock = Lock(redis, key, default_lock_ttl=10)
        assert lock.state == RELEASED
        assert lock.ttl == 10
        lock.lock('name1')
        assert lock.ttl == 10


def test_lock_global_value():
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock1 = Lock(redis, key, default_lock_ttl=1)
        assert not lock1.is_locked()

        lock1.lock("name1")

        lock2 = Lock(redis, key, default_lock_ttl=10)
        assert lock2.is_locked()
        assert lock1.get_locked_inside() == lock2.get_locked_inside()
        assert lock1.state == lock2.state

        lock1.break_in()
        assert lock2.is_locked()
        assert lock1.get_locked_inside() == lock2.get_locked_inside()
        assert lock1.state == lock2.state

        lock2.unlock()

        assert not lock1.is_locked()
        assert lock1.get_locked_inside() == lock2.get_locked_inside()
        assert lock1.state == lock2.state
