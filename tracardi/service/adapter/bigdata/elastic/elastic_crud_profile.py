from typing import Optional

from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.flat_profile import FlatProfile
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.helpers.crud_profile_helper import load_by_id

logger = get_logger(__name__)


class ElasticCrudProfileAdapter(ElasticAdapter):
    async def load_flat_profile_by_id(self, profile_id: str) -> Optional[FlatProfile]:
        record = await load_by_id(profile_id)
        if record is None:
            return None
        return FlatProfile.from_es_storage_record(record)
