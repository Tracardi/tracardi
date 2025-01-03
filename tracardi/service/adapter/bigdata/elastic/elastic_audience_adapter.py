from typing import List

from tracardi.common.logging.log_handler import get_logger
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.helpers.audience_helper import load_by_primary_ids

logger = get_logger(__name__)

class ElasticAudienceAdapter(ElasticAdapter):

    async def load_by_primary_ids(self, profile_ids: List[str], size):
        return await load_by_primary_ids(profile_ids, size)