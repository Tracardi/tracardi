from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends

from .. import config
from ..domain.scope import Scope
from ..errors.errors import NullResponseError
from ..filters.elastic import filter_scope
from ..globals.authentication import get_current_user
from ..globals.elastic_client import elastic_client

router = APIRouter(
    prefix="/scope",
    # dependencies=[Depends(get_current_user)]
)


@router.get("/{id}")
def scope_get(id: str, elastic=Depends(elastic_client)):
    scope_index = config.index['scopes']
    result = elastic.get(scope_index, id)
    return {
        "meta": {
            "id": result['_source']['doc']["_id"],
        },
        "doc": result['_source']['doc']
    }


@router.post("/")
def insert_scope(scope: Scope, elastic=Depends(elastic_client)):
    scope_index = config.index['scopes']
    scope = {
        '_id': scope.get_id(),
        'name': scope.name,
        'hostname': scope.host,
    }
    return elastic.insert(scope_index, [scope])


@router.post("/select")
async def segment_select(request: Request, elastic=Depends(elastic_client)):
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

        scope_index = config.index['scopes']

        result = elastic.scan(scope_index, q)

        return list(filter_scope(result))

    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
