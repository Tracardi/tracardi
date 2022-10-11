from tracardi.domain.storage_record import StorageRecord
from tracardi.service.storage.factory import storage_manager


def load():
    return storage_manager('version').load(id="0")


def save(version: dict):
    return storage_manager('version').upsert(version, replace_id=True)


async def load_by_version_and_name(version: str, name: str) -> StorageRecord:
    result = await storage_manager('version').query({
        "query": {
            "bool": {
                "must": [
                    {"term": {"version": version}},
                    {"term": {"name": name}}
                ]
            }
        }
    })

    return result.first()
