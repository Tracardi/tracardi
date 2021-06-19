from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException, Depends

from .auth.authentication import get_current_user
from ..domain.enum.indexes_histogram import IndexesHistogram
from ..domain.enum.indexes_search import IndexesSearch
from ..domain.index import Index
from ..domain.sql_query import SqlQuery
from ..domain.time_range_query import DatetimeRangePayload

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.post("/{index}/select", tags=["generic", "event", "profile", "source", "rule", "session", "flow", "segment"])
async def select_by_sql(index: IndexesSearch, query: Optional[SqlQuery] = None):
    try:
        elastic_index = Index(index.value)
        if query is None:
            query = SqlQuery()
        return await elastic_index.search(query.where, query.limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{index}/select/range", tags=["generic", "event", "profile", "source", "rule", "session", "flow", "segment"])
async def time_range_with_sql(index: IndexesHistogram, query: DatetimeRangePayload):
    try:
        elastic_index = Index(index.value)
        return await elastic_index.time_range(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{index}/select/histogram", tags=["generic", "event", "profile", "source", "rule", "session", "flow", "segment"])
async def histogram_with_sql(index: IndexesHistogram, query: DatetimeRangePayload):
    try:
        elastic_index = Index(index.value)
        return await elastic_index.histogram(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
