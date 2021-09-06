from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor


async def save_session(session: Session, profile: Profile, persist_session: bool = True):
    if persist_session and (session.operation.new or session.profile is None or session.profile.id != profile.id):
        # save only profile Entity
        session.profile = Entity(id=profile.id)
        return await StorageFor(session).index().save()
    else:
        return BulkInsertResult()
