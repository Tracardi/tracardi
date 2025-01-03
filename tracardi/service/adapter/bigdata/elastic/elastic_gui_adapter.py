from typing import List

from tracardi.common.logging.log_handler import get_logger
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.helpers.gui_helper import load_profiles_by_segments

logger = get_logger(__name__)

class ElasticGuiAdapter(ElasticAdapter):

    async def load_profiles_by_segments(self, segments: List[str], condition: str = 'must') -> dict:
        records = await load_profiles_by_segments(segments, condition=condition)
        return records.dict()