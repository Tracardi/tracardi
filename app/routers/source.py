from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends

from .. import config
from ..domain.source import Source
from ..errors.errors import NullResponseError
from ..filters.elastic import filter_source
from ..globals.authentication import get_current_user
from ..globals.elastic_client import elastic_client

router = APIRouter(
    prefix="/source",
    # dependencies=[Depends(get_current_user)]
)


@router.get("/{id}")
def source_get(id: str, elastic=Depends(elastic_client)):
    source_index = config.index['sources']
    result = elastic.get(source_index, id)
    return result['_source']


@router.post("/")
def insert_source(source: Source, elastic=Depends(elastic_client)):
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


@router.post("/select")
async def source_select(request: Request, elastic=Depends(elastic_client)):
    try:
        q = await request.body()
        q = q.decode('utf-8')
        if q:
            q = {
                "query": {
                    "regexp": {
                        "doc.name": {
                            "value": q + ".*",
                            "flags": "ALL",
                            "max_determinized_states": 1000,
                        }
                    }
                }
            }
        else:
            q = {
                "query": {
                    "match_all": {}
                }
            }

        source_index = config.index['sources']

        result = elastic.scan(source_index, q)

        return list(filter_source(result))

    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
