from tracardi.service.storage.elastic.dal.raw import count


async def count_entities(query: dict = None):
    return await count('entity', query)
