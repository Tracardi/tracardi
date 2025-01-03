from typing import List, Dict

from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.helpers.analytics_event_helper import aggregate_event_type, \
    aggregate_source_by_type, aggregate_source_by_tags, aggregate_event_tag, get_avg_process_time, \
    aggregate_event_status, aggregate_event_device_geo, aggregate_event_os_name, aggregate_event_channels, \
    aggregate_event_resolution, aggregate_events_by_source, load_events_avg_requests, \
    aggregate_events_by_type_and_source
from tracardi.service.adapter.bigdata.elastic.helpers.analytics_profile_helper import aggregate_profile_events_by_type, \
    aggregate_profile_events_by_field, aggregate_profile_events, load_events_by_profile_and_field, \
    load_modified_top_profiles, count_profile_duplicates

logger = get_logger(__name__)


class ElasticAnalyticsAdapter(ElasticAdapter):

    async def aggregate_event_types_from_db(self) -> List[Dict[str, str]]:
        return await aggregate_event_type()

    async def aggregate_events_by_source_and_type(self, source_id, time_span):
        return await aggregate_source_by_type(source_id, time_span)

    async def aggregate_events_by_source_and_tags(self, source_id, time_span):
        return await aggregate_source_by_tags(source_id, time_span)

    async def aggregate_event_tags_from_db(self) -> List[Dict[str, str]]:
        return await aggregate_event_tag()

    async def load_event_avg_process_time(self):
        return await get_avg_process_time()

    async def load_events_avg_requests(self):
        return await load_events_avg_requests()

    async def aggregate_event_statuses_from_db(self):
        return await aggregate_event_status()

    async def aggregate_event_devices_geo_from_db(self):
        return await aggregate_event_device_geo()

    async def aggregate_event_os_names_from_db(self):
        return await aggregate_event_os_name()

    async def aggregate_event_channels_from_db(self):
        return await aggregate_event_channels()

    async def aggregate_event_resolutions_from_db(self):
        return await aggregate_event_resolution()

    async def aggregate_events_by_source_from_db(self, buckets_size: int):
        return await aggregate_events_by_source(buckets_size=buckets_size)

    # Profile

    async def load_events_by_profile_and_field(self, profile_id: str, field: str, table: bool = False):
        return await load_events_by_profile_and_field(profile_id, field, table)

    async def load_modified_top_profiles(self, size) -> dict:
        result = await load_modified_top_profiles(size)
        return result.dict()

    async def count_profile_duplicates(self, profile_ids: List[str]):
        return await count_profile_duplicates(profile_ids)

    async def aggregate_profile_events_by_type(self, profile_id: str, bucket_name) -> StorageAggregateResult:
        return await aggregate_profile_events_by_type(profile_id, bucket_name)

    async def aggregate_profile_events_by_field(self, profile_id: str, field: str, bucket_name: str,
                                                size: int = 15) -> StorageAggregateResult:
        return await aggregate_profile_events_by_field(profile_id, field, bucket_name, size)

    async def aggregate_profile_events(self, profile_id: str, aggregate_query: dict) -> StorageAggregateResult:
        return await aggregate_profile_events(profile_id, aggregate_query)

    async def aggregate_events_by_type_and_source(self) -> List[dict]:
        def _get_data(result):
            for by_type in result.aggregations('by_type').buckets():
                row = {'type': by_type['key'], 'source': []}
                for bucket in by_type['by_source']['buckets']:
                    row['source'].append({
                        "id": bucket['key'],
                        "count": bucket['doc_count']
                    })
                yield row

        result = await aggregate_events_by_type_and_source()
        return list(_get_data(result))
