from time import sleep

import redis

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.adapter.cache_adaper_selector import cache_adapter

_cache = cache_adapter()
logger = get_logger(__name__)

def wait_for_redis_connection():
    no_of_tries = 10
    while True:
        try:

            if no_of_tries < 0:
                logger.error(f"Could not connect to redis")
                exit(1)

            if _cache.ping():
                break

        except redis.exceptions.ConnectionError as e:
            logger.warning(str(e))
            no_of_tries -= 1
            sleep(1)