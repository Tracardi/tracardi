from typing import Optional

from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, storage_manager


async def save_session(session: Session, profile: Optional[Profile], profile_less, persist_session: bool = True):
    if persist_session:
        if profile_less is False:
            if session.operation.new or session.profile is None or (isinstance(session.profile, Entity)
                                                                    and isinstance(profile, Entity)
                                                                    and session.profile.id != profile.id):
                # save only profile Entity
                session.profile = Entity(id=profile.id)

        return await StorageFor(session).index().save()

    return BulkInsertResult()


async def load(id: str) -> Session:
    return await StorageFor(Entity(id=id)).index("session").load(Session)


async def refresh():
    return await storage_manager('session').refresh()


async def flush():
    return await storage_manager('session').flush()
