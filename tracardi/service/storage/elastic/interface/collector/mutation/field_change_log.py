from tracardi.service.storage.elastic.dal.field_update_log import upsert


async def save_field_changes(data: list):
    await upsert(data)
