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

scheduled_locally = False


class PostponedCall:

    def __init__(self, profile_id, callable_coroutine, *args):
        self.profile_id = profile_id
        self.callable_coroutine = callable_coroutine
        self.args = args
        self.wait = 60

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

            # should the execution be postponed. If there was no second call then postpone is false.
            if postpone_flag_cache.get(self.profile_id, False):
                # postpone call. Postpone flag is true
                self._schedule_for_later(loop)
                logger.info(f"Execution postponed for profile {self.profile_id}")
                # set postpone flag to false. It can be set to true again if there is another call.
                postpone_flag_cache.set(self.profile_id, False)
            else:
                # it is not postponed - run it now
                self._run_scheduled()
                # clean cache
                postpone_flag_cache.reset(self.profile_id)
                schedule_flag_cache.reset(self.profile_id)

        except Exception as e:
            logger.error(str(e))

    def _schedule(self, loop):
        self._schedule_for_later(loop)
        # mark as scheduled globally
        schedule_flag_cache.set(self.profile_id, True)

    def run(self, loop):
        scheduled_globally = schedule_flag_cache.get(self.profile_id, False)

        if not scheduled_globally or not scheduled_locally:
            # if there is no schedule global or local. Schedule for the first time.
            self._schedule(loop)
        else:
            # if this is a second call then postpone
            postpone_flag_cache.set(self.profile_id, True)
