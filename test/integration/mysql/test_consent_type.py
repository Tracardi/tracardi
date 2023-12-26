from uuid import uuid4

import asyncio
import pytest

from tracardi.context import ServerContext, Context
from tracardi.domain.consent_type import ConsentType
from tracardi.service.storage.mysql.service.consent_type_service import ConsentTypeService

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_consent_types(event_loop):
    asyncio.set_event_loop(event_loop)
    with ServerContext(Context(production=True)):  # Required context
        service = ConsentTypeService()
        consent_type_id = str(uuid4())
        try:
            await service.insert(ConsentType(id=consent_type_id, name='Test Consent', description='Description', default_value='grant'))
            consent_types = await service.load_all()
            assert any(consent_type.id == consent_type_id for consent_type in consent_types.rows)

            consent_type = await service.load_by_id(consent_type_id)
            assert consent_type.rows.id == consent_type_id

            keys = await service.load_keys()
            assert any(id == consent_type_id for id in keys.rows)

        finally:
            await service.delete_by_id(consent_type_id)

