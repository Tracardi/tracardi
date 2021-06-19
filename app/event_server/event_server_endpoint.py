from pprint import pprint

from fastapi import APIRouter
from fastapi import HTTPException
from app.domain.record.event_debug_record import EventDebugRecord
from app.domain.value_object.tracker_payload_result import TrackerPayloadResult
from app.domain.payload.tracker_payload import TrackerPayload
from app.exceptions.exception import TracardiException
from app.process_engine.rules_engine import RulesEngine
from app.event_server.service.source_cacher import source_cache
from app.service.storage.collection_crud import CollectionCrud


router = APIRouter()


# @router.post("/event_server", tags=['event server'])
# async def context(tracker_payload: TrackerPayload):
#     try:
#
#         source = await source_cache.validate_source(source_id=tracker_payload.source.id)
#
#         profile, session, events, result = await tracker_payload.collect()
#
#         result = TrackerPayloadResult(**result.dict())
#
#         # Save to log
#         await result.storage().save()
#
#         return {
#             "profile": profile.dict(exclude={"properties": {"private": ...}}),
#             "source": source.dict(exclude={"tracker": ...}),
#             "metadata": {
#                 "time": tracker_payload.metadata.time,
#                 "result": result
#             }
#         }
#
#     except TracardiException as e:
#         raise HTTPException(detail=str(e), status_code=500)


@router.post("/track", tags=['event server'])
async def track(tracker_payload: TrackerPayload):
    try:
        source = await source_cache.validate_source(source_id=tracker_payload.source.id)

        result = await tracker_payload.process()
        result['source'] = source.dict(include={"consent": ...})

        return result

    except TracardiException as e:
        raise HTTPException(detail=str(e), status_code=500)
