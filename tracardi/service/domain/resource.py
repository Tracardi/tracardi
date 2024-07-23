from tracardi.domain.resource import Resource
from tracardi.service.storage.mysql.interface import resource_dao


async def save_record(resource: Resource):
    return await resource_dao.insert_resource(resource)


async def load(id: str) -> Resource:
    return await resource_dao.load_resource_by_id_with_error(id)
