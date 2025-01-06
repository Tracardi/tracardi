from typing import Tuple

from tracardi.service.adapter.bigdata.elastic.client.elastic_client import ElasticClient

def _acknowledged(result):
    return 'acknowledged' in result and result['acknowledged'] is True

class ElasticTemplate:

    def __init__(self, client: ElasticClient):
        self._client = client

    async def insert(self, template_name: str, mapping: dict) -> Tuple[bool, dict]:
        result = await self._client.put_index_template(template_name, mapping)
        return _acknowledged(result), result

    async def exists(self, name):
        return await self._client.exists_index_template(name=name)

    async def delete(self, name: str) -> bool:
        if await self._client.exists_index_template(name):
            result = await self._client.delete_index_template(name)
            if not _acknowledged(result):
                return False
        return True