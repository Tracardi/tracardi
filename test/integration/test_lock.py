from time import sleep

from tracardi.context import ServerContext, Context
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.locking import Lock, unlock_tolerance


def test_lock_ttl():
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock = Lock(redis, key, default_lock_ttl=10)
        assert lock.is_locked() is False
        lock.lock("name1", lock_ttl=1)
        assert lock.is_locked() is True
        sleep(2)
        assert lock.is_locked() is False
        lock.unlock("name1")

def test_lock_expires():
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock = Lock(redis, key, default_lock_ttl=10)
        assert lock.expires() == 10 + unlock_tolerance
        lock.lock('name1')
        assert lock.expires() == 10 + unlock_tolerance


def test_lock_2():
    with ServerContext(Context(production=False)):
        redis = RedisClient()
        key = Lock.get_key("namespace:", "profile", "10")
        lock = Lock(redis, key, default_lock_ttl=10)
        lock.lock("name1", lock_ttl=1)
        lock.lock("name2", lock_ttl=1)
        print(lock.get_lock_metadata())