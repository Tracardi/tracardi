from collections import defaultdict
from time import sleep

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from .auth.authentication import get_current_user
from .grouper import search
from ..domain.entity import Entity
from ..domain.segment import Segment
from ..domain.segments import Segments
from ..domain.value_object.bulk_insert_result import BulkInsertResult
from ..event_server.service.persistence_service import PersistenceService
from ..service.storage.elastic_storage import ElasticStorage

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.get("/segment/{id}")
async def get_segment(id: str):
    try:
        entity = Entity(id=id)
        return await entity.storage('segment').load(Segment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/segment/{id}")
async def delete_segment(id: str):
    try:
        entity = Entity(id=id)
        return await entity.storage('segment').delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/segments/refresh", tags=["segment"])
async def refresh_segments():
    service = PersistenceService(ElasticStorage(index_key='segment'))
    return await service.refresh()


@router.get("/segments", tags=["segment"])
async def get_segments(query: str = None):
    try:
        sources = Segments()
        result = await sources.bulk().load()
        total = result.total
        result = [Segment.construct(Segment.__fields_set__, **r) for r in result]

        # Filtering
        if query is not None and len(query) > 0:
            query = query.lower()
            if query:
                result = [r for r in result if
                          query in r.name.lower() or (r.eventType is not None and search(query, [r.eventType]))]

        # Grouping
        groups = defaultdict(list)
        for segment in result:  # type: Segment
            if isinstance(segment.eventType, list):
                for group in segment.eventType:
                    groups[group].append(segment)
            elif isinstance(segment.eventType, str):
                groups[segment.eventType].append(segment)
            else:
                groups["Global"].append(segment)

        # Sort
        groups = {k: sorted(v, key=lambda r: r.name, reverse=False) for k, v in groups.items()}

        return {
            "total": total,
            "grouped": groups
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/segment", tags=["segment"], response_model=BulkInsertResult)
async def upsert_source(segment: Segment):
    sleep(2)
    try:
        return await segment.storage().save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
