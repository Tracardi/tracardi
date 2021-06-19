import asyncio
from uuid import uuid4

from app.domain.consent import Consent
from app.domain.profile import Profile
from app.domain.session import Session
from app.domain.source import Source


async def main(obj):
    obj = obj(id=str(uuid4()))
    result = await obj.storage().load()
    assert result is None
    await obj.storage().save()
    consent_loaded = await obj.storage().load()
    assert consent_loaded.id == obj.id
    await obj.storage().delete()
    result = await obj.storage().load()
    assert result is None

loop = asyncio.get_event_loop()
for o in [
    Consent,
    Profile,
    Session,
    # Flow,
    # Segment,
    Source,
    # UserConsent
]:
    loop.run_until_complete(main(o))
loop.close()
