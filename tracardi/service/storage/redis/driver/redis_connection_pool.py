from tracardi.config import RedisConfig
from redis import ConnectionPool

from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)


def get_redis_connection_pool(redis_config: RedisConfig) -> ConnectionPool:
    uri = redis_config.get_redis_with_password()
    logger.info(f"Connecting redis via pool at {uri}")
    return ConnectionPool.from_url(
        uri,
        max_connections=20,
        health_check_interval=30,
    )
