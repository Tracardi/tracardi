from tracardi.service.storage.elastic.dal import log as log_db


async def save_log(data):
    await log_db.save(data)
