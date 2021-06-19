import elasticsearch

from app.domain.value_object.bulk_insert_result import BulkInsertResult
from app.service.storage import index
from app.service.storage.elastic import Elastic


class ElasticStorage:

    def __init__(self, index_key):
        self.storage = Elastic.instance()
        self.index = index.resources[index_key].name

    async def load(self, id) -> [dict, None]:
        try:
            result = await self.storage.get(self.index, id)
            output = result['_source']
            output['id'] = result['_id']
            return output
        except elasticsearch.exceptions.NotFoundError:
            return None

    async def create(self, payload) -> BulkInsertResult:
        return await self.storage.insert(self.index, payload)

    async def delete(self, id):
        return await self.storage.delete(self.index, id)

    async def search(self, query):
        return await self.storage.search(self.index, query)

    async def translate(self, sql):
        return await self.storage.translate(sql)

    async def load_by(self, field, value):
        query = {
            "query": {
                "term": {
                    field: {"value": value}
                }
            }
        }
        return await self.search(query)

    async def delete_by(self, field, value):
        query = {
            "query": {
                "term": {
                    field: {"value": value}
                }
            }
        }
        return await self.storage.delete_by_query(self.index, query)
