import logging
from datetime import datetime
from typing import Optional, List

import elasticsearch

from tracardi.config import tracardi
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.storage_record import StorageRecord
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.entity import Entity
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.factory import StorageFor, storage_manager, StorageCrud


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def save_sessions(profiles: List[Session]):
    return await storage_manager("session").upsert(profiles)


async def update_session_duration(session: Session):
    storage = storage_manager("session")
    index = storage.storage.get_storage_index(session)

    record = {
        "doc": {
            "id": session.id,
            "profile": {
                "id": session.profile.id
            } if session.profile else None,
            "metadata": {
                "time": {
                    "insert": session.metadata.time.insert,
                    "update": datetime.utcnow(),
                    "duration": session.metadata.time.duration
                }
            }
        },
        'doc_as_upsert': True
    }
    try:
        result = await storage.update_by_id(id=session.id, record=record, index=index, retry_on_conflict=3)
        return result
    except elasticsearch.exceptions.ConflictError as e:
        logger.warning(f"Minor Session Conflict Error: Last session duration could not be updated. "
                       f"This may happen  when there is a rapid stream of events. Reason: {str(e)}")


async def save_session(session: Session, profile: Optional[Profile], persist_session: bool = True):
    if persist_session:
        if isinstance(session, Session):
            if session.operation.new:
                # Add new profile id to session if it does not exist, or profile id in session is different from
                # the real profile id.
                if session.profile is None or (isinstance(session.profile, Entity)
                                               and isinstance(profile, Entity)
                                               and session.profile.id != profile.id):
                    # save only profile Entity
                    if profile is not None:
                        session.profile = Entity(id=profile.id)
                session_index = StorageFor(session).index()  # type: StorageCrud
                return await session_index.save()
            else:
                # Update session duration
                await update_session_duration(session)

    return BulkInsertResult()


async def save(session: Session):
    return await StorageFor(session).index().save()


async def exist(id: str) -> bool:
    return await storage_manager("session").exists(id)


async def load_by_id(id: str) -> Optional[Session]:
    session_record = await storage_manager("session").load(id)
    if session_record is None:
        return None
    session = session_record.to_entity(Session)

    return session


async def load_duplicates(id: str):
    return await storage_manager('session').query({
        "query": {
            "term": {
                "_id": id
            }
        },
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    })


async def delete(id: str):
    return await storage_manager('session').delete(id)


async def refresh():
    return await storage_manager('session').refresh()


async def flush():
    return await storage_manager('session').flush()


async def get_nth_last_session(profile_id: str, n: int) -> Optional[StorageRecord]:
    query = {
        "query": {
            "term": {"profile.id": profile_id}
        },
        "size": 11,
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    }

    records = await storage_manager('session').query(query)

    if len(records) >= n:
        return StorageRecord.build_from_elastic(records.row(n - 1))

    return None


async def count(query: dict = None):
    return await storage_manager('session').count(query)
