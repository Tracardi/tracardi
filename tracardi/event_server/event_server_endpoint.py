from fastapi import APIRouter
from fastapi import HTTPException

from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.exceptions.exception import TracardiException
from tracardi.event_server.service.source_cacher import source_cache

router = APIRouter()


@router.post("/track", tags=['event server'])
async def track(tracker_payload: TrackerPayload):
    try:
        source = await source_cache.validate_source(source_id=tracker_payload.source.id)

        result, profile = await tracker_payload.process()
        result['source'] = source.dict(include={"consent": ...})

        return result

    except TracardiException as e:
        raise HTTPException(detail=str(e), status_code=500)
