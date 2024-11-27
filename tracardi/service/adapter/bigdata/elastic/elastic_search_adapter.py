from typing import Set

from tracardi.config import elastic
from tracardi.domain.query_result import QueryResult
from tracardi.domain.time_range_query import DatetimeRangePayload

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.adapter.bigdata.elastic.cache.field_mapping import load_cached_field_names, \
    load_cached_column_values
from tracardi.service.adapter.bigdata.elastic.client.elastic_client import ElasticClient
from tracardi.service.adapter.bigdata.elastic.client.elastic_index import ElasticIndex
from tracardi.service.adapter.bigdata.elastic.helpers.search_engine_helper import SqlSearchQueryEngine
from tracardi.service.wf.field_mappings_cache import FieldMapper

logger = get_logger(__name__)


class ElasticSearchAdapter:

    def __init__(self):
        kwargs = ElasticClient.get_elastic_config(elastic)
        self._client = ElasticClient(**kwargs)
        self._params = {}

    def index(self, index) -> ElasticIndex:
        return ElasticIndex(self._client, index)

    # Search

    async def search_in_time_range(self, index_type_name: str, query: DatetimeRangePayload) -> QueryResult:
        engine = SqlSearchQueryEngine(self.index(index_type_name))
        return await engine.time_range(query)

    async def search_histogram_in_time_range(self, index_type_name: str, query: DatetimeRangePayload,
                                             group_by: str = None) -> QueryResult:
        engine = SqlSearchQueryEngine(self.index(index_type_name))
        return await engine.histogram(query, group_by)

    async def search_with_query(self, index_type_name: str, query: str, start: int = 0, limit: int = 0) -> dict:
        engine = SqlSearchQueryEngine(self.index(index_type_name))
        result = await engine.search(query, start, limit)
        return result.dict()

    # Fields Autocomplete

    async def get_defined_columns_in_table(self, table: str) -> set:
        db_mappings = await load_cached_field_names(self.index(table))
        set_of_db_mappings = set(db_mappings)
        set_of_db_mappings.update(FieldMapper().get_field_mapping(table))
        return set(sorted(list(set_of_db_mappings)))

    async def get_values_from_table_colum(self, table: str, column: str, limit=100) -> Set[str]:
        return await load_cached_column_values(self.index(table), column, limit)
