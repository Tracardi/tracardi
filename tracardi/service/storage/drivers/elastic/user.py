from tracardi.service.storage.factory import storage_manager
from uuid import UUID
from tracardi.service.sha1_hasher import SHA1Encoder
from typing import List, Union
from tracardi.domain.user import User


async def add_user(id: UUID, username: str, password: str, full_name: str, email: str, roles: List[str], disabled: bool):
    return await storage_manager("user").upsert({
        "id": str(id),
        "username": SHA1Encoder.encode(username),
        "password": SHA1Encoder.encode(password),
        "full_name": full_name,
        "email": email,
        "roles": roles,
        "disabled": disabled
    })


async def del_user(id: UUID):
    return await storage_manager("user").delete(str(id))


async def get_by_login_data(username: str, password: str) -> Union[User, None]:
    result = (await storage_manager("user").query({
        "query": {
            "bool": {
                "must": [
                    {"term": {"username": SHA1Encoder.encode(username)}},
                    {"term": {"password": SHA1Encoder.encode(password)}}
                ]
            }
        }
    }))["hits"]["hits"]
    if result:
        return User(**result[0]["_source"])
    return None


async def check_if_exists(username: str, id: UUID) -> bool:
    return bool((await storage_manager("user").query({
        "query": {
            "bool": {
                "should": [
                    {"term": {"username": SHA1Encoder.encode(username)}},
                    {"term": {"_id": str(id)}}
                ],
                "minimum_should_match": 1
            }
        }
    }))["hits"]["total"]["value"])
