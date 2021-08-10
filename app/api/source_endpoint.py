from collections import defaultdict
from time import sleep
from typing import Dict

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from .auth.authentication import get_current_user
from .grouper import search
from ..domain.source import Source, SourceRecord
from ..domain.entity import Entity
from ..domain.enum.indexes_source_bool import IndexesSourceBool
from ..domain.sources import Sources
from ..domain.storage_result import StorageResult
from ..domain.value_object.bulk_insert_result import BulkInsertResult
from ..event_server.service.persistence_service import PersistenceService
from ..service.storage.elastic_storage import ElasticStorage

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.get("/sources/types", tags=["source"], response_model=dict)
async def get_source_types() -> dict:
    """
    Returns a list of source types. Each source requires a source type to define what kind of data is
    that source holding.
    """

    try:
        return {"total": 3, "result": ["web-page", "storage", "queue"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", tags=["source"])
async def list_sources():
    try:
        sources = Sources()
        result = await sources.bulk().load()
        total = result.total
        result = [SourceRecord.construct(Source.__fields_set__, **r).decode() for r in result]

        return {
            "total": total,
            "result": list(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/by_tag", tags=["source"])
async def list_sources(query: str = None):
    try:
        sources = Sources()
        result = await sources.bulk().load()
        total = result.total
        result = [SourceRecord.construct(Source.__fields_set__, **r).decode() for r in result]

        # Filtering
        if query is not None and len(query) > 0:
            query = query.lower()
            if query:
                result = [r for r in result if query in r.name.lower() or search(query, r.type)]

        # Grouping
        groups = defaultdict(list)
        for source in result:  # type: Source
            if isinstance(source.origin, list):
                for group in source.origin:
                    groups[group].append(source)
            elif isinstance(source.origin, str):
                groups[source.origin].append(source)

        # Sort
        groups = {k: sorted(v, key=lambda r: r.name, reverse=False) for k, v in groups.items()}

        return {
            "total": total,
            "grouped": groups
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/source/{id}/{type}/on", tags=["source"], response_model=dict)
async def set_source_property_on(id: str, type: IndexesSourceBool):
    try:
        entity = Entity(id=id)

        record = await entity.storage("source").load(SourceRecord)  # type: SourceRecord

        source = record.decode()
        source_data = source.dict()
        source_data[type.value] = True
        source = Source.construct(_fields_set=source.__fields_set__, **source_data)
        record = SourceRecord.encode(source)

        return await record.storage().save()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/source/{id}/{type}/off", tags=["source"], response_model=dict)
async def set_source_property_off(id: str, type: IndexesSourceBool):
    try:
        entity = Entity(id=id)

        record = await entity.storage("source").load(SourceRecord)  # type: SourceRecord

        source = record.decode()
        source_data = source.dict()
        source_data[type.value] = False
        source = Source.construct(_fields_set=source.__fields_set__, **source_data)
        record = SourceRecord.encode(source)

        return await record.storage().save()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/source/{id}", tags=["source"], response_model=Source)
async def get_source_by_id(id: str) -> Source:
    """
    Returns source data with given id.

    """

    try:
        entity = Entity(id=id)
        record = await entity.storage("source").load(SourceRecord)  # type: SourceRecord
        return record.decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/source", tags=["source"], response_model=BulkInsertResult)
async def upsert_source(source: Source):
    sleep(1)
    try:
        record = SourceRecord.encode(source)
        return await record.storage().save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/source/{id}", tags=["source"], response_model=dict)
async def delete_source(id: str):
    try:
        entity = Entity(id=id)
        return await entity.storage("source").delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources/refresh", tags=["source"])
async def refresh_sources():
    service = PersistenceService(ElasticStorage(index_key='source'))
    return await service.refresh()
