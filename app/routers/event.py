from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from ..errors.errors import NullResponseError
from ..filters.datagrid import filter_event
from ..globals.authentication import get_current_user
from ..globals.context_server import context_server_via_uql

router = APIRouter(
    prefix="/event",
    # dependencies=[Depends(get_current_user)]
)


@router.get("/{id}")
async def event_get(id: str, uql=Depends(context_server_via_uql)):
    q = f"SELECT EVENT WHERE id=\"{id}\""

    try:
        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        return result["list"][0]
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select")
async def event_select(request: Request, uql=Depends(context_server_via_uql)):
    try:
        q = await request.body()
        q = q.decode('utf-8')
        if q:
            q = f"SELECT EVENT WHERE {q}"
        else:
            q = "SELECT EVENT LIMIT 20"

        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        result = list(filter_event(result))
        return result
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
