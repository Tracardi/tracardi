from typing import Optional

from tracardi.common.logging.log_handler import get_logger
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.helpers.plugin_event_helper import get_nth_last_event, \
    load_active_profile_by_field

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