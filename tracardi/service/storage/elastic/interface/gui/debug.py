from tracardi.service.storage.elastic.dal import raw as raw_db


async def get_indices_list():
    """
    This one returns raw data as it is elastic specific.
    """
    return await raw_db.indices()
