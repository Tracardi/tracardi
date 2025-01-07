from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from adapter.bigdata.elastic.client.elastic_client import ElasticClient

from tracardi.domain.event import Event
from tracardi.domain.flat_event import FlatEvent

from adapter.bigdata.elastic.model.storage_record import StorageRecord
from adapter.bigdata.elastic.logging.logger import get_logger
from adapter.bigdata.elastic.client.elastic_index import index
from typing import List, Optional, Union, Set

logger = get_logger(__name__)


async def load_event(client: ElasticClient, id: str) -> Optional[StorageRecord]:
    return await index(client, "event").load(id)


async def save(client: ElasticClient, events: Union[List[FlatEvent], List[Event], Set[Event]], exclude=None) -> Union[BulkInsertResult, List[BulkInsertResult]]:
    return await index(client, "event").save(events, exclude=exclude)


async def delete_by_id(client: ElasticClient, id: str) -> dict:
    ci = index(client, "event")
    # Delete in all indices
    return await ci.delete(id, index=ci.index.get_multi_storage_alias())
