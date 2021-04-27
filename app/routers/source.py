import elasticsearch
from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends

from .. import config
from ..domain.source import Source
from ..errors.errors import NullResponseError, convert_exception_to_json
from ..filters.elastic import filter_source
from ..globals.authentication import get_current_user
from ..globals.elastic_client import elastic_client

router = APIRouter(
    prefix="/source",
    dependencies=[Depends(get_current_user)]
)


@router.get("/{id}")
def source_get(id: str, elastic=Depends(elastic_client)):
    try:
        source_index = config.index['sources']
        result = elastic.get(source_index, id)
        return result['_source']
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=convert_exception_to_json(e))

    except elasticsearch.exceptions.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=convert_exception_to_json(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))


@router.delete("/{id}")
async def source_delete(id: str,
                        elastic=Depends(elastic_client)):
    try:
        index = config.index['sources']
        return elastic.delete(index, id)
    except elasticsearch.exceptions.NotFoundError:
        # todo logging
        print("Record `{}` not found in elastic.".format(id))


@router.post("/")
def insert_source(source: Source, elastic=Depends(elastic_client)):
    try:
        source_index = config.index['sources']
        source = {
            '_id': source.get_id(),
            'itemId': source.get_id(),
            'itemType': "source",
            'name': source.name,
            'hostname': source.hostname,
            'metadata': {
                'scope': source.scope,
                'systemTags': [],
                'tags': [],
                'enabled': True
            }
        }
        return elastic.insert(source_index, [source])
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=convert_exception_to_json(e))

    except elasticsearch.exceptions.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=convert_exception_to_json(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))


@router.post("/select")
async def source_select(request: Request, elastic=Depends(elastic_client)):
    try:
        q = await request.body()
        q = q.decode('utf-8')
        if q:
            q = {
                "size": 20,
                "query": {
                    "regexp": {
                        "name": {
                            "value": q + ".*",
                            "flags": "ALL",
                            "max_determinized_states": 1000,
                        }
                    }
                }
            }
        else:
            q = {
                "size": 20,
                "query": {
                    "match_all": {}
                }
            }

        source_index = config.index['sources']

        result = elastic.search(source_index, q)
        return list(filter_source(result['hits']['hits']))

    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=convert_exception_to_json(e))

    except elasticsearch.exceptions.NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=convert_exception_to_json(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))
