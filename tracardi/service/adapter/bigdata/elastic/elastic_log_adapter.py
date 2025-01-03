from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.adapter.bigdata.elastic.client.elastic_query import get_query_to_load_by_field_and_value, \
    get_agg_query_for_log_levels

from tracardi.service.adapter.bigdata.collector_protocol import CollectorProtocol
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.common.time.date import now_in_utc


class ElasticLogAdapter(ElasticAdapter, CollectorProtocol):

    async def load_logs_by_flow(self, flow_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[List[dict], int]:
        query = get_query_to_load_by_field_and_value(field="flow_id", value=flow_id, limit=limit, sort=sort)
        result = await self.core.query('log', query)
        return list(result), result.total

    async def load_logs_by_profile(self, profile_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[
        List[dict], int]:
        query = get_query_to_load_by_field_and_value(field="profile_id", value=profile_id, limit=limit, sort=sort)
        result = await self.core.query('log', query)
        return list(result), result.total

    async def load_logs_by_event(self, event_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[
        List[dict], int]:
        query = get_query_to_load_by_field_and_value(field="event_id", value=event_id, limit=limit, sort=sort)
        result = await self.core.query('log', query)
        return list(result), result.total

    async def load_logs_by_node(self, node_id: str, sort: List[Dict[str, Dict]] = None, limit=30) -> Tuple[List[dict], int]:
        query = get_query_to_load_by_field_and_value(field="node_id", value=node_id, limit=limit, sort=sort)
        result = await self.core.query('log', query)
        return list(result), result.total

    async def load_group_logs_by_level(self, date_from: Optional[datetime] = None) -> Dict[str, int]:
        if date_from is None:
            date_from = now_in_utc() - timedelta(days=30)

        query = get_agg_query_for_log_levels(date_from)

        result = await self.core.query('log', query)
        buckets = result.aggregations('error_levels').buckets()
        return {item['key']: item['doc_count'] for item in buckets}

    async def save_logs(self, logs) -> BulkInsertResult:
        return await self.core.save('log',logs)
