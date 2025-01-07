from typing import Optional

from adapter.bigdata.elastic.model.storage_record import StorageRecord
from adapter.bigdata.elastic.logging.logger import get_logger
from adapter.bigdata.elastic.client.elastic_client import ElasticClient
from adapter.bigdata.elastic.client.elastic_index import index
from adapter.bigdata.elastic.client.elastic_query import get_query_to_load_profile_by_id

logger = get_logger(__name__)


async def load_profile(client: ElasticClient, profile_id: str, **kwargs) -> Optional[StorageRecord]:
    query = get_query_to_load_profile_by_id(profile_id)

    profile_records = await index(client, 'profile').query(query)
    if profile_records.total <= 0:
        return None

    if profile_records.total > 1:
        logger.warning(
            "Profile {} id duplicated in the database. It will be merged with APM worker.".format(profile_id))

    profile_record = profile_records.first()

    if profile_record is None:
        return None

    return profile_record
