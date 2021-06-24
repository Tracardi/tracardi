from time import sleep

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from .auth.authentication import get_current_user
from ..domain.entity import Entity
from ..domain.segment import Segment
from ..domain.segments import Segments
from ..domain.value_object.bulk_insert_result import BulkInsertResult

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
                result = [r for r in result if query in r.name.lower()]

        return {
            "total": total,
            "result": result
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
