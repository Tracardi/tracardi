from time import sleep
from typing import Optional
import asyncio
from tracardi.service.postpone_call import PostponedCall
from threading import Thread


class PostponeCacheMock:

    def __init__(self):
        self.cache = {}

    def exists(self, profile_id):
        return profile_id not in self.cache

    def get(self, profile_id) -> bool:
        if profile_id not in self.cache:
            self.cache[profile_id] = '1'
            return False

        return True

    def set(self, profile_id):
        self.cache[profile_id] = '1'

    def reset(self, profile_id):
        del self.cache[profile_id]


class InstanceCacheMock:

    def __init__(self):
        self.cache = {}

    def exists(self, profile_id):
        return profile_id in self.cache

    def get_instance(self, profile_id, instance_id) -> Optional[str]:
        if not self.exists(profile_id):
            self.cache[profile_id] = instance_id
            return None

        return self.cache[profile_id]

    def set_instance(self, profile_id, instance_id):
        self.cache[profile_id] = instance_id

    def reset(self, profile_id):
        del self.cache[profile_id]


_global_postpone_flag = PostponeCacheMock()
_global_schedule_flag = PostponeCacheMock()
_instance_cache = InstanceCacheMock()


def test_should_postpone_calls_on_different_instances():

    profile_id = "test"

    async def call(*args):
        print(args)

    async def instance1(loop):
        postpone = PostponedCall(profile_id, call, "instance-1", "0-arg1", "0-arg2")
        postpone.global_postpone_flag = _global_postpone_flag
        postpone.global_schedule_flag = _global_schedule_flag
        postpone.instance_cache = _instance_cache
        postpone.wait = 2
        postpone.run(loop, force_recreate=True)
        await asyncio.sleep(5)

    async def instance2(loop):
        postpone2 = PostponedCall(profile_id, call, "instance-2", "1-arg1", "1-arg2")
        postpone2.global_postpone_flag = _global_postpone_flag
        postpone2.global_schedule_flag = _global_schedule_flag
        postpone2.instance_cache = _instance_cache
        postpone2.wait = 1
        postpone2.run(loop, force_recreate=True)
        await asyncio.sleep(5)

    async def instance3(loop):
        postpone2 = PostponedCall(profile_id, call, "instance-2", "3-arg1", "3-arg2")
        postpone2.global_postpone_flag = _global_postpone_flag
        postpone2.global_schedule_flag = _global_schedule_flag
        postpone2.instance_cache = _instance_cache
        postpone2.wait = 1
        postpone2.run(loop, force_recreate=True)
        await asyncio.sleep(5)

    def main1():
        loop1 = asyncio.new_event_loop()
        try:
            loop1.run_until_complete(instance1(loop1))
        except KeyboardInterrupt:
            pass
        finally:
            print("Closing Loop1")
            loop1.close()

    def main2():
        loop2 = asyncio.new_event_loop()
        try:
            loop2.run_until_complete(instance2(loop2))
        except KeyboardInterrupt:
            pass
        finally:
            print("Closing Loop2")
            loop2.close()

    def main3():
        loop2 = asyncio.new_event_loop()
        try:
            loop2.run_until_complete(instance3(loop2))
        except KeyboardInterrupt:
            pass
        finally:
            print("Closing Loop3")
            loop2.close()

    thread1 = Thread(target=main1)
    thread2 = Thread(target=main2)
    thread3 = Thread(target=main3)

    thread1.start()
    sleep(0.5)
    thread2.start()
    sleep(0.1)
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()
