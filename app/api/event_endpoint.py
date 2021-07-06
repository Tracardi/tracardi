from time import sleep

from fastapi import APIRouter, Depends
from fastapi import HTTPException

from .auth.authentication import get_current_user
from ..domain.entity import Entity
from ..event_server.service.persistence_service import PersistenceService
from ..service.storage.elastic_storage import ElasticStorage
from ..domain.event import Event
from ..domain.events import Events
from ..domain.profile import Profile

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.get("/events/metadata/type", tags=["event", "event server"])
async def event_types():
    events = Events()
    result = await events.bulk().uniq_field_value("type.keyword")
    return {
        "total": result.total,
        "result": list(result)
    }


@router.get("/event/{id}", tags=["event", "event server"])
async def get_event(id: str):
    try:
        event = Entity(id=id)
        # Loads TrackerPayload as it has broader data
        full_event = await event.storage("event").load(Event)  # type: Event
        if full_event is None:
            raise HTTPException(detail="Event {} does not exist.".format(id), status_code=404)

        profile = Entity(id=full_event.profile.id)
        full_event.profile = await profile.storage("profile").load(Profile)

        query = {
            "query": {
                "match": {
                    "events.ids": id,
                }
            }
        }

        index = PersistenceService(ElasticStorage(index_key="stat-log"))
        event_result = await index.filter(query)

        return {
            "event": full_event,
            "result": list(event_result)[0] if event_result.total == 1 else None
        }

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/event/{id}", tags=["event", "event server"])
async def delete_event(id: str):
    try:
        event = Entity(id=id)
        return await event.storage("event").delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
