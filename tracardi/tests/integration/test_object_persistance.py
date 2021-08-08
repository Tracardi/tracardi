from time import sleep

import pytest
from uuid import uuid4

from tracardi.domain.consent import Consent
from tracardi.domain.entity import Entity
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session


@pytest.mark.asyncio
async def test_domain_persistance():
    async def main(obj):
        obj = obj(id=str(uuid4()))
        result = await obj.storage().load()
        assert result is None
        await obj.storage().save()
        sleep(1)
        object_loaded = await obj.storage().load()
        assert object_loaded.id == obj.id
        await obj.storage().delete()
        sleep(1)
        result = await obj.storage().load()
        assert result is None

    for o in [
        Profile,
        Session,
    ]:
        await main(o)


@pytest.mark.asyncio
async def test_entity_persistance():
    async def main(obj, index):
        entity = Entity(id=str(uuid4()))
        result = await entity.storage(index).load(obj)
        assert result is None
        await entity.storage(index).save()
        sleep(1)
        object_loaded = await entity.storage(index).load(obj)
        assert object_loaded.id == entity.id
        result = await entity.storage(index).load_by("id", entity.id)
        for r in result:
            assert r['id'] == entity.id
        await entity.storage(index).delete()
        sleep(1)
        result = await entity.storage(index).load(obj)
        assert result is None

    for o, index in [
        (Consent, 'consent'),
        (Profile, 'profile'),
        (Session, 'session')
    ]:
        await main(o, index)
