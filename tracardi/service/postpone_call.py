import asyncio
import logging

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


# todo this works only in one threaded env.

class PostponedCallCache:

    def __init__(self):
        self.postpone_profile_cache = {}
        self.schedule_profile_cache = {}

    def get_postpone(self, profile_id, default_value) -> bool:
        if profile_id not in self.postpone_profile_cache:
            self.postpone_profile_cache[profile_id] = default_value

        return self.postpone_profile_cache[profile_id]

    def set_postpone(self, profile_id, value):
        self.postpone_profile_cache[profile_id] = value

    def get_schedule(self, profile_id, default_value) -> bool:
        if profile_id not in self.schedule_profile_cache:
            self.schedule_profile_cache[profile_id] = default_value

        return self.schedule_profile_cache[profile_id]

    def set_schedule(self, profile_id, value):
        self.schedule_profile_cache[profile_id] = value

    def reset(self, profile_id):
        del self.postpone_profile_cache[profile_id]
        del self.schedule_profile_cache[profile_id]


cache = PostponedCallCache()


class PostponedCall:

    def __init__(self, profile_id, callable_coroutine, *args):
        self.profile_id = profile_id
        self.callable_coroutine = callable_coroutine
        self.args = args
        self.wait = 60

    def _postpone_call(self, loop):
        try:
            if cache.get_postpone(self.profile_id, False):
                loop.call_later(self.wait, self._postpone_call, loop)
                cache.set_postpone(self.profile_id, False)
            else:
                asyncio.ensure_future(self.callable_coroutine(*self.args))
                cache.reset(self.profile_id)
        except Exception as e:
            logger.error(str(e))

    def run(self, loop):
        if cache.get_schedule(self.profile_id, False) is False:
            loop.call_later(self.wait, self._postpone_call, loop)
            cache.set_schedule(self.profile_id, True)
        else:
            cache.set_postpone(self.profile_id, True)
