from tracardi.service.storage.elastic.dal.field_update_log import load_by_type


async def load_field_changes_by_type(type: str) -> dict:
    result = await load_by_type(type)
    return result.dict()

