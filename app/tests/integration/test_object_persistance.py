import pytest
from uuid import uuid4

from app.domain.consent import Consent
from app.domain.profile import Profile
from app.domain.session import Session


@pytest.mark.asyncio
async def test_persistance():
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

    for o in [
        Consent,
        Profile,
        Session,
    ]:
        await main(o)
