import asyncio
import logging

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.postpone_cache_multi_threaded import PostponeCache

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

schedule_flag_cache = PostponeCache("schedule-flag")
postpone_flag_cache = PostponeCache("postpone-flag")
instance_cache = PostponeCache("exec-instance-cache")

scheduled_locally = False


class PostponedCall:

    def __init__(self, profile_id, callable_coroutine, instance_id, *args):
        self.profile_id = profile_id
        self.callable_coroutine = callable_coroutine
        self.args = args
        self.wait = 60
        self.instance_id = instance_id

    def _schedule_for_later(self, loop):

        # We must keep info about the loop.call_later being called in scheduled_locally variable, as if the instance
        # dies (loop.call_later is cancelled) and there is a global flag that loop.call_later is running but locally it
        # is not. Sho we must recreate it.

        global scheduled_locally
        loop.call_later(self.wait, self._postpone_call, loop)
        scheduled_locally = True

    def _run_scheduled(self):
        global scheduled_locally
        asyncio.ensure_future(self.callable_coroutine(*self.args))
        scheduled_locally = False

    def _postpone_call(self, loop):
        try:
            global_postpone_flag = postpone_flag_cache.get(self.profile_id)

            # should the execution be postponed. If there was no second call then postpone is None.
            if global_postpone_flag is None:
                # it is not postponed - run it now

                global_instance = instance_cache.get(self.profile_id)
                if global_instance == self.instance_id:
                    # run it only if the local instance is the same as global schedule instance
                    self._run_scheduled()
                else:
                    logger.info(f"Execution on instance {self.instance_id} discarded. Execution passed to {global_instance}")

                # clean cache
                postpone_flag_cache.reset(self.profile_id)
                schedule_flag_cache.reset(self.profile_id)
            else:
                # postpone call. Postpone flag is true
                self._schedule_for_later(loop)
                logger.info(f"Execution postponed for profile {self.profile_id}. Execute on instance {self.instance_id}")
                # delete postpone flag. It can be set again if there is another call.
                postpone_flag_cache.reset(self.profile_id)
                schedule_flag_cache.set(self.profile_id)

        except Exception as e:
            logger.error(str(e))

    def run(self, loop):
        # set current instance
        instance_cache.set_instance(self.profile_id, self.instance_id)

        # set global schedule flag
        global_schedule_flag = schedule_flag_cache.get_instance(self.profile_id, self.instance_id)

        if not scheduled_locally:
            # if there is no schedule local. Schedule for the first time.
            self._schedule_for_later(loop)

        if global_schedule_flag is None:
            # mark as scheduled globally
            schedule_flag_cache.set_instance(self.profile_id, self.instance_id)
        else:
            # if this is a second call then postpone
            postpone_flag_cache.set_instance(self.profile_id, self.instance_id)
