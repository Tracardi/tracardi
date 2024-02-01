from tracardi.config import RedisConfig
from redis import ConnectionPool

from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


def get_redis_connection_pool(redis_config: RedisConfig) -> ConnectionPool:
    if redis_config.redis_password:
        pool = ConnectionPool(host=redis_config.host,
                              port=redis_config.port,
                              password=redis_config.redis_password,
                              max_connections=20)
    else:
        pool = ConnectionPool(host=redis_config.host,
                              port=redis_config.port,
                              max_connections=20)

    return pool
