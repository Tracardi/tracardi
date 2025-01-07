from datetime import datetime

from typing import Optional, Tuple, List

from adapter.bigdata.elastic.logging.logger import get_logger
from tracardi.domain.entity_record import EntityRecord
from tracardi.domain.remote_system_integration_id import RemoteSystemIntegrationId
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from .helpers.entity_helper import delete_by_id, load, load_entity_types, upsert, load_integration_id, \
    save_integration_id, upsert_entity

logger = get_logger(__name__)


def _acknowledged(result):
    return 'acknowledged' in result and result['acknowledged'] is True


class ElasticEntityAdapter(ElasticAdapter):

    async def create_entity(self, index, mapping):
        index = f"entity-{index}"
        result = await self.client.create_index(index, mapping.model_dump(by_alias=True))
        if 'error' in result:
            raise ValueError(f"{result['error']}")
        return _acknowledged(result)

    async def get_entity_mapping(self, index):
        index = f"entity-{index}"
        result = await self.client.get_mapping(index)
        return result[index]

    async def load(self, entity_id) -> Optional[EntityRecord]:
        return await load(entity_id)

    async def delete_by_id(self, entity_id: str) -> dict:
        return await delete_by_id(entity_id)

    async def load_entity_types(self) -> Tuple[List[dict], int]:
        return await load_entity_types()

    async def load_integration_id(self, profile_id: str, system_name: str) -> List[RemoteSystemIntegrationId]:
        result = await load_integration_id(profile_id, system_name)
        return result.to_domain_objects(RemoteSystemIntegrationId)

    async def upsert(self, entity: EntityRecord) -> BulkInsertResult:
        return await upsert(entity)

    async def refresh(self):
        return await self.core.refresh('entity')

    async def flush(self):
        return await self.core.flush('entity')

    async def count(self, query: dict = None):
        return await self.core.count('entity', query)

    async def save_integration_id(self, profile_id: str, system_name: str, integration_id: str,
                                  data: Optional[dict] = None):
        return await save_integration_id(profile_id, system_name, integration_id, data)

    async def save_entity(self, type: str, entity_id: str, referenced_profile_id: str, key: str, properties: dict,
                          traits: dict,
                          due_date: Optional[datetime] = None, expiration_date: Optional[datetime] = None) -> Tuple[
        BulkInsertResult, EntityRecord]:
        return await upsert_entity(type, entity_id, referenced_profile_id, key, properties, traits, due_date,
                                   expiration_date)
