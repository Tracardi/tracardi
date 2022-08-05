from tracardi.domain.storage_result import StorageResult
from tracardi.service.storage.factory import storage_manager
from tracardi.service.sha1_hasher import SHA1Encoder
from typing import List, Optional
from tracardi.domain.user import User


async def refresh():
    return await storage_manager("user").refresh()


async def flush():
    return await storage_manager("user").flush()


async def add_user(user: User):
    user.encode_password()
    return await storage_manager("user").upsert(user.dict())


async def search_by_name(start: int, limit: int, name: str):
    query = {
        "from": start,
        "size": limit,
        "query": {
            "wildcard": {
                "full_name": f"{name}*"
            }
        }
    }

    result = []

    for record in (await storage_manager("user").query(query=query))["hits"]["hits"]:
        user = User(**record["_source"])
        result.append({**user.dict(exclude={"token"}), "expired": user.is_expired()})

    return result


async def update_user(user: User):
    return await storage_manager("user").upsert(user.dict())


async def delete_user(id: str):
    return await storage_manager("user").delete(id)


async def get_by_id(id: str):
    return await storage_manager("user").load(id)


async def load(start: int, limit: int):
    return await storage_manager("user").load_all(start, limit)


async def get_by_credentials(email: str, password: str) -> Optional[User]:
    result = (await storage_manager("user").query({
        "query": {
            "bool": {
                "must": [
                    {"term": {"email": email}},
                    {"term": {"password": SHA1Encoder.encode(password)}},
                    {"term": {"disabled": False}}
                ]
            }
        }
    }))["hits"]["hits"]

    if result:
        return User(**result[0]["_source"])
    return None


async def search_by_token(token: str) -> StorageResult:
    query = {
        "query": {"term": {"token": str(token)}}
    }
    result = await storage_manager("user").query(query=query)
    return StorageResult(result)


async def search_by_role(role: str) -> StorageResult:
    query = {
        "query": {"term": {"roles": str(role)}}
    }
    result = await storage_manager("user").query(query=query)
    return StorageResult(result)


async def check_if_exists(email: str) -> bool:
    return await storage_manager("user").exists(id=email)
