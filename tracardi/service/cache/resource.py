from typing import Optional

from tracardi.config import memory_cache
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.domain.resource import Resource
from tracardi.service.storage.mysql.interface import resource_dao
from tracardi.exceptions.log_handler import get_logger

logger = get_logger(__name__)

@AsyncCache(memory_cache.resource_load_cache_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_resource_via_cache(resource_id: str) -> Optional[Resource]:
    try:
        return await resource_dao.load_resource_by_id_with_error(resource_id)
    except Exception as e:
        logger.warning(f"Resource {resource_id} not found. Details: {e}")
        return None