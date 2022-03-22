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


class PostponeCache:

    def __init__(self):
        self.cache = {}

    def get(self, profile_id, default_value) -> bool:
        if profile_id not in self.cache:
            self.cache[profile_id] = default_value

        return self.cache[profile_id]

    def set(self, profile_id, value):
        self.cache[profile_id] = value

    def reset(self, profile_id):
        del self.cache[profile_id]

