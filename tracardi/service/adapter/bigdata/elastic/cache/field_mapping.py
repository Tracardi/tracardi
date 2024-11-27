from typing import List, Set

from tracardi.domain.storage.index_mapping import IndexMapping

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.adapter.bigdata.elastic.client.elastic_index import ElasticIndex
from tracardi.service.adapter.bigdata.elastic.client.elastic_query import get_query_for_unique_values_from_field
from tracardi.service.decorators.async_cache import AsyncCache

logger = get_logger(__name__)


@AsyncCache(60,
            timeout=.5,
            max_one_cache_fill_every=.1,
            return_cache_on_error=True
            )
async def load_cached_field_names(index: ElasticIndex) -> List[str]:
    """
    Returns E.G: {data.contact.address.country, ...}
    """
    mapping = IndexMapping(await index.get_mapping())
    return mapping.get_field_names()


@AsyncCache(60,
            timeout=.5,
            max_one_cache_fill_every=.1,
            return_cache_on_error=True
            )
async def load_cached_column_values(index: ElasticIndex, column, limit=100) -> Set[str]:
    """
    return E.G. {'Kiribati', 'Jamaica', 'Netherlands',...} Values from column.
    """
    query = get_query_for_unique_values_from_field(field=column, limit=limit)
    result = await index.query(query)
    return {item.get("key_as_string", item.get("key", None)) for item in result.aggregations("fields").buckets()}
