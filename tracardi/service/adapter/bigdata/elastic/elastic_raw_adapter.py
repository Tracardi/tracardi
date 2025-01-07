from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from .helpers.raw_helper import count_by_query
from tracardi.service.storage.index import Resource
from elasticsearch import NotFoundError

def _acknowledged(result):
    return 'acknowledged' in result and result['acknowledged'] is True


class ElasticRawAdapter(ElasticAdapter):

    async def count_by_query(self, index: str, query: str, time_span: int):
        return await count_by_query(index, query, time_span)

    async def get_field_names_for_index(self, index: str):
        mapping = await self.client.get_mapping(index)
        mapping = mapping[index]
        return mapping.get_field_names()

    async def task_status(self, task_id):
        return await self.client.get_task(task_id)

    async def health(self):
        return await self.client.health()

    async def get_settings(self):
        return await self.client.cluster.get_settings(
            flat_settings=True,
            include_defaults=True
        )

    async def remove_index(self, index: str) -> bool:
        if await self.client.exists_index(index):
            result = await self.client.remove_index(index)
            if _acknowledged(result):
                return True
        return False

    async def get_alias(self, name: str):
        return self.client.get_alias(name)

    async def update_aliases(self, body):
        return await self.client.update_aliases(body=body)

    async def remove_alias(self, alias_index):
        if await self.client.exists_alias(alias_index, index=None):
            result = await self.client.delete_alias(alias=alias_index, index="_all")
            if _acknowledged(result):
                return True
        return False

    async def alias_exists(self, alias_index, index=None):
        return self.client.exists_alias(alias_index, index=index)

    async def alias_create(self, alias_index, target_index):
        if await self.client.exists_index(target_index) and not await self.client.exists_alias(alias_index, index=None):
            return await self.client.update_aliases(body={
                "actions": [
                    {
                        "add": {
                            "index": target_index,
                        }
                    }
                ]
            })

    async def remove_template(self, template_name):
        return await self.template.delete(template_name)

    async def template_exists(self, template_name):
        return await self.template.exists(template_name)

    async def template_create(self, template_name, template_map):
        return await self.template.insert(template_name, template_map)

    async def list_indices(self, index="*"):
        return await self.client.list_indices(index)

    async def index_exists(self, target_index: str):
        return await self.client.exists_index(target_index)

    async def index_create(self, target_index: str, mappings: dict):
        return await self.client.create_index(target_index, mappings)

    async def count_all_indices_by_alias(self):
        """
        Missing indices are returned as count = 0
        """

        for name, index in Resource().resources.items():
            try:
                count = await self.index(name).count()
                yield name, count['count']
            except NotFoundError:
                yield name, 0

    async def get_mapping(self, index: str):
        return await self.client.get_mapping(index=index)

    async def set_mapping(self, index, mapping: dict):
        return await self.client.set_mapping(index, mapping=mapping)