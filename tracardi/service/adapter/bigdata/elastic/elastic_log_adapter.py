from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

from tracardi.config import elastic
from tracardi.service.adapter.bigdata.elastic.client.elastic_client import ElasticClient
from tracardi.service.adapter.bigdata.elastic.client.elastic_index import ElasticIndex
from tracardi.service.adapter.bigdata.elastic.client.elastic_query import get_query_to_load_by_field_and_value, \
    get_agg_query_for_log_levels

from com_tracardi.protocol.bigdata.collector_protocol import CollectorProtocol
from tracardi.service.utils.date import now_in_utc


class ElasticLogAdapter(CollectorProtocol):

    def __init__(self):
        kwargs = ElasticClient.get_elastic_config(elastic)
        self._client = ElasticClient(**kwargs)
        self._params = {}

    def index(self, index) -> ElasticIndex:
        return ElasticIndex(self._client, index)

    async def load_by_flow(self, flow_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[List[dict], int]:
        query = get_query_to_load_by_field_and_value(field="flow_id", value=flow_id, limit=limit, sort=sort)
        result = await self.index('log').query(query)
        return list(result), result.total

    async def load_by_profile(self, profile_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[
        List[dict], int]:
        query = get_query_to_load_by_field_and_value(field="profile_id", value=profile_id, limit=limit, sort=sort)
        result = await self.index('log').query(query)
        return list(result), result.total

    async def load_by_event(self, event_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[
        List[dict], int]:
        query = get_query_to_load_by_field_and_value(field="event_id", value=event_id, limit=limit, sort=sort)
        result = await self.index('log').query(query)
        return list(result), result.total

    async def load_by_node(self, node_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[List[dict], int]:
        query = get_query_to_load_by_field_and_value(field="node_id", value=node_id, limit=limit, sort=sort)
        result = await self.index('log').query(query)
        return list(result), result.total

    async def group_by_level(self, date_from: Optional[datetime] = None) -> Dict[str, int]:
        if date_from is None:
            date_from = now_in_utc() - timedelta(days=30)

        query = get_agg_query_for_log_levels(date_from)

        result = await self.index('log').query(query)
        buckets = result.aggregations('error_levels').buckets()
        return {item['key']: item['doc_count'] for item in buckets}
