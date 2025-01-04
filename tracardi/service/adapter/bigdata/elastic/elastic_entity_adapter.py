from typing import Optional, Tuple, List

from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.entity_record import EntityRecord
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from .helpers.entity_helper import delete_by_id, load, load_entity_types, upsert

logger = get_logger(__name__)


class ElasticEntityAdapter(ElasticAdapter):
    async def load(self, entity_id) -> Optional[EntityRecord]:
        return await load(entity_id)

    async def delete_by_id(self, entity_id: str) -> dict:
        return await delete_by_id(entity_id)

    async def load_entity_types(self) -> Tuple[List[dict], int]:
       return await load_entity_types()

    async def upsert(self, entity: EntityRecord) -> BulkInsertResult:
        return await upsert(entity)

    async def refresh(self):
        return await self.core.refresh('entity')

    async def flush(self):
        return await self.core.flush('entity')

    async def count(self, query: dict = None):
        return await self.core.count('entity', query)
