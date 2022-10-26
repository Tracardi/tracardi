import asyncio
import logging

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.postpone_cache_multi_threaded import PostponeCache, InstanceCache
from tracardi.service.singleton import Singleton

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

global_schedule_flag = PostponeCache("schedule-flag")
global_postpone_flag = PostponeCache("postpone-flag")
instance_cache = InstanceCache("exec-instance-cache")


class LockPool(metaclass=Singleton):

    def __init__(self):
        self.pool = set()

    def schedule(self, id: str):
        self.pool.add(id)

    def unschedule(self, id: str):
        self.pool.discard(id)

    def is_scheduled(self, id: str) -> bool:
        return id in self.pool

    def __len__(self):
        return len(self.pool)


class PostponedCall:

    def __init__(self, profile_id, callable_coroutine, instance_id, *args):
        self.instance_cache = instance_cache
        self.global_postpone_flag = global_postpone_flag
        self.global_schedule_flag = global_schedule_flag
        self.profile_id = profile_id
        self.callable_coroutine = callable_coroutine
        self.args = args
        self.wait = 60
        self.instance_id = instance_id
        self.lock_pool = LockPool()

    def _schedule_for_later(self, loop):

        # We must keep info about the loop.call_later being called in lock_pool variable, as if the instance
        # dies (loop.call_later is cancelled) and there is a global flag that loop.call_later is running, but locally it
        # is not. So we must recreate it.

        loop.call_later(self.wait, self._execute, loop)
        self.lock_pool.schedule(self.profile_id)

    def _run_scheduled(self):
        asyncio.ensure_future(self.callable_coroutine(*self.args))
        self.lock_pool.unschedule(self.profile_id)

    def _execute(self, loop):
        global_instance = self.instance_cache.get_instance(self.profile_id, None)
        if global_instance != self.instance_id:
            logger.info(
                f"Execution DISCARDED. Execution passed from worker instance {self.instance_id} to instance {global_instance}")
            return

        try:
            # should the execution be postponed. If there was no second call then postpone is None.
            if self.global_postpone_flag.get(self.profile_id) is False:
                logger.info(f"Profile {self.profile_id} destination sync RUNS from instance {self.instance_id}.")
                # it is not postponed - run it now
                self._run_scheduled()

                # clean cache
                self.global_postpone_flag.reset(self.profile_id)
                self.global_schedule_flag.reset(self.profile_id)
                self.instance_cache.reset(self.profile_id)

            else:
                # postpone call. Postpone flag is true
                self._schedule_for_later(loop)
                logger.info(
                    f"Execution on worker instance {self.instance_id} POSTPONED for {self.wait}s for profile {self.profile_id}")
                # delete postpone flag. It can be set again if there is another call.
                self.global_postpone_flag.reset(self.profile_id)

        except Exception as e:
            logger.error(str(e))

    def run(self, loop, force_recreate=False):
        # set current instance
        self.instance_cache.set_instance(self.profile_id, self.instance_id)

        if not self.lock_pool.is_scheduled(self.profile_id) or force_recreate:
            # if there is no schedule local. Schedule for the first time.
            self._schedule_for_later(loop)

        if self.global_schedule_flag.get(self.profile_id) is False:
            # mark as scheduled globally
            self.global_schedule_flag.set(self.profile_id)
        else:
            # if this is a second call then postpone
            self.global_postpone_flag.set(self.profile_id)
