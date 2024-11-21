from time import sleep
from uuid import uuid4

import pytest

from tracardi.context import Context, ServerContext
from tracardi.service.tracking.locking import async_mutex, Lock


@pytest.mark.asyncio
async def test_async_mutex():
    with ServerContext(Context(tenant="a", production=True)):
        profile_key = Lock.get_key("text-lck", "profile", str(uuid4()))
        profile_lock = Lock(profile_key, default_lock_ttl=60)  # If withing 3 sec not processed will auto unlock
        async with async_mutex(profile_lock, name='test_locking', break_after_time=.1) as m:
            print(m)