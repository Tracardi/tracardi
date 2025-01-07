from typing import Optional

from tracardi.common.logging.log_handler import get_logger
from adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from adapter.bigdata.elastic.helpers.plugin_event_helper import get_nth_last_event, \
    load_active_profile_by_field, aggregate_event_by_field_within_time, count_events_by_type

logger = get_logger(__name__)


class ElasticPluginAdapter(ElasticAdapter):

    async def load_nth_last_event(self, event_type: str, offset: int, profile_id: Optional[str] = None):
        return await get_nth_last_event(
            profile_id=profile_id,
            event_type=event_type,
            n=(-1) * offset
        )

    async def load_active_profile_by_field(self, field: str, value: str, start: int = 0, limit: int = 100):
        return await load_active_profile_by_field(field, value, start, limit)

    async def aggregate_event_by_field_within_time(self, profile_id: str, field_id: str, span_in_sec: int, metric,
                                                   event_type):
        return await aggregate_event_by_field_within_time(
            profile_id,
            field_id,
            span_in_sec,
            metric,
            event_type
        )

    async def count_events_by_type(self, profile_id: str, event_type_id: str, span_in_sec: int):
        return await count_events_by_type(
            profile_id,
            event_type_id,
            span_in_sec
        )
