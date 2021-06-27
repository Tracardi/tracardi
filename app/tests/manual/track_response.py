import asyncio
from uuid import uuid4
import app.domain.entity as entity
from app.domain.profile import Profile
from app.domain.profile_traits import ProfileTraits
from app.domain.response import Response, ResponseItem
from app.event_server.service.persistence_service import PersistenceService
from app.service.storage.elastic_storage import ElasticStorage
from app.service.storage.index import resources


async def response_data():
    profile_id = str(uuid4())

    profile = Profile(id=profile_id, traits=ProfileTraits(public={"a": 1}))
    await profile.storage().save()

    pr = entity.Entity(id=profile_id)
    print(await pr.storage('profile').load(Profile))

    response_id = str(uuid4())
    response_entity = Response(id=response_id,
                               data=[ResponseItem(index='profile', slices=['traits.public'])])

    await response_entity.storage().save()

    response_entity = entity.Entity(id=response_id)

    response = await response_entity.storage('response').load(Response)  # type: Response
    print(response)
    for response_item in response.data:
        index = response_item.index
        slices = response_item.slices
        if index in resources and resources[index].rel is not None:
            storage = PersistenceService(ElasticStorage(index_key=index))
            result = await storage.load_by(resources[index].rel, profile.id)
            print(result)


asyncio.run(response_data())
