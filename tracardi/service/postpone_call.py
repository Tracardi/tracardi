import asyncio
import logging

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.postpone_cache_single_thread import PostponeCache

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

schedule_flag_cache = PostponeCache()
postpone_flag_cache = PostponeCache()


class PostponedCall:

    def __init__(self, profile_id, callable_coroutine, *args):
        self.profile_id = profile_id
        self.callable_coroutine = callable_coroutine
        self.args = args
        self.wait = 60

    def _postpone_call(self, loop):
        try:

            # should the execution be postponed. If there was no second call then postpone is false.
            if postpone_flag_cache.get(self.profile_id, False):
                # postpone call. Postpone flag is true
                loop.call_later(self.wait, self._postpone_call, loop)
                # set postpone flag to false. It can be set to true again if there is another call.
                postpone_flag_cache.set(self.profile_id, False)
            else:
                # it is not postponed - run it now
                asyncio.ensure_future(self.callable_coroutine(*self.args))
                # clean cache
                postpone_flag_cache.reset(self.profile_id)
                schedule_flag_cache.reset(self.profile_id)

        except Exception as e:
            logger.error(str(e))

    def run(self, loop):
        if schedule_flag_cache.get(self.profile_id, False) is False:
            # if there is no schedule or schedule is False. Schedule for the first time.
            loop.call_later(self.wait, self._postpone_call, loop)
            # mark as scheduled
            schedule_flag_cache.set(self.profile_id, True)
        else:
            # if this is a second call then postpone
            postpone_flag_cache.set(self.profile_id, True)
