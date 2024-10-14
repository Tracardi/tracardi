from collections import defaultdict
from time import time


class Timer:

    def __init__(self, max_timeout: int = 60 * 60):
        self.time_db = defaultdict(float)
        self.max_timeout = max_timeout

    def reset_timer(self, key):
        self.time_db[key] = time()

    def get_time(self, key) -> float:
        return self.time_db.get(key, 0.0)

    def get_passed_time(self, key) -> float:
        return time() - self.get_time(key)

    def is_time_over(self, key, max_time) -> bool:
        key_time = self.time_db.get(key, 0)

        if key_time == 0:
            self.reset_timer(key)

        passed_time = time() - self.time_db.get(key, 0)

        return passed_time > max_time or passed_time > self.max_timeout

