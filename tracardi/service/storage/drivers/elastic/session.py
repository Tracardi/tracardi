from datetime import datetime
from typing import Optional, List

from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.storage_record import StorageRecord
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, storage_manager


async def save_sessions(profiles: List[Session]):
    return await storage_manager("session").upsert(profiles)


async def update_session_duration(session: Session):
    await storage_manager("session").update_document(id=session.id, record={
        "metadata": {
            "time": {
                "update": datetime.utcnow(),
                "duration": session.metadata.time.duration
            }
        }
    }, retry_on_conflict=3)


async def save_session(session: Session, profile: Optional[Profile], persist_session: bool = True):
    if persist_session:

        if isinstance(session, Session):
            if session.operation.new:
                # Add new profile id to session if it does not exist, or profile id in session is different then
                # the real profile id.
                if session.profile is None or (isinstance(session.profile, Entity)
                                               and isinstance(profile, Entity)
                                               and session.profile.id != profile.id):
                    # save only profile Entity
                    session.profile = Entity(id=profile.id)
                return await StorageFor(session).index().save()
            else:
                # Update session duration
                await update_session_duration(session)

    return BulkInsertResult()


async def save(session: Session):
    return await StorageFor(session).index().save()


async def exist(id: str) -> bool:
    return await storage_manager("session").exists(id)


async def load(id: str) -> Optional[Session]:
    return await StorageFor(Entity(id=id)).index("session").load(Session)  # type: Optional[Session]


async def delete(id: str):
    return await storage_manager('session').delete(id)


async def refresh():
    return await storage_manager('session').refresh()


async def flush():
    return await storage_manager('session').flush()


async def get_nth_last_session(profile_id: str, n: int) -> Optional[StorageRecord]:
    result = await storage_manager('session').query({
        "query": {
            "term": {"profile.id": profile_id}
        },
        "size": 11,
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    })

    records = result["hits"]["hits"]  # type: List[dict]

    if len(records) >= n:
        return StorageRecord.build_from_elastic(records[n - 1])

    return None


async def count(query: dict = None):
    return await storage_manager('session').count(query)
