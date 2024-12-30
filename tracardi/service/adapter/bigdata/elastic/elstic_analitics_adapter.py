from typing import List, Dict

from tracardi.common.logging.log_handler import get_logger
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.helpers.analytics_helper import aggregate_event_type, \
    aggregate_source_by_type, aggregate_source_by_tags, aggregate_event_tag, get_avg_process_time, \
    aggregate_event_status, aggregate_event_device_geo, aggregate_event_os_name, aggregate_event_channels, \
    aggregate_event_resolution, aggregate_events_by_source

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