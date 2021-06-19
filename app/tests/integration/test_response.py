from uuid import uuid4

import pytest

from app.domain.entity import Entity
from app.domain.profile import Profile
from app.domain.profile_properties import ProfileProperties
from app.domain.response import Response
# import app.service.storage.crud as crud
from app.service.storage.index import resources


@pytest.mark.asyncio
async def test_response_data():
    pass
    # profile_id = str(uuid4())
    #
    # profile = Profile(id=profile_id, properties=ProfileProperties(public={"a":1}))
    # await profile.storage().save()
    #
    # response_id = str(uuid4())
    # response_entity = Response(id=response_id, data=['profile'])
    # await response_entity.storage().save()
    #
    # response_entity = Entity(id=response_id)
    #
    # response = await response_entity.storage('response').load(Response)  # type: Response
    # for index in response.data:
    #     if index in resources and resources[index].rel is not None and resources[index].object is not None:
    #         # storage = crud.EntityStorageCrud(resources[index].name, entity=resources[index].object)
    #         # result = storage.load_by(resources[index].rel, profile.id)
    #         pass

