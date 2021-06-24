import copy

from fastapi import APIRouter
from fastapi import HTTPException

from app.domain.payload.event_payload import EventPayload
from app.domain.payload.tracker_payload import TrackerPayload
from app.domain.segment import Segment
from app.domain.segments import Segments
from app.exceptions.exception import TracardiException
from app.event_server.service.source_cacher import source_cache
from app.process_engine.tql.condition import Condition
from app.process_engine.tql.utils.dictonary import flatten

router = APIRouter()


@router.post("/track", tags=['event server'])
async def track(tracker_payload: TrackerPayload):
    try:
        source = await source_cache.validate_source(source_id=tracker_payload.source.id)

        result, profile = await tracker_payload.process()
        result['source'] = source.dict(include={"consent": ...})

        if profile.metadata.updated:

            # todo move to invoke
            # todo cache segments
            flat_payload = flatten(copy.deepcopy(profile.dict()))

            for event in tracker_payload.events:  # type: EventPayload
                segments = await Segments.storage().load_by('eventType.keyword', event.type)
                for segment in segments:
                    try:
                        segment = Segment(**segment)
                        print("eval", segment.condition, Condition.evaluate(segment.condition, flat_payload), flat_payload)
                        if Condition.evaluate(segment.condition, flat_payload):
                            print("Segmentation", segment.get_id())
                            profile.segments.append(segment.get_id())
                            pass
                            # todo save segment
                    except Exception as e:
                        print('Condition `{}` could not be evaluated. The following error was raised: `{}`'.format(
                            segment.condition, str(e).replace("\n", " ")))
                        # todo log exception
                        pass
                print(segments)

        return result

    except TracardiException as e:
        raise HTTPException(detail=str(e), status_code=500)
