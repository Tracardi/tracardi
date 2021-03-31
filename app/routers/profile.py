from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from ..errors.errors import NullResponseError
from ..filters.datagrid import filter_profile
from ..globals.authentication import get_current_user
from ..globals.context_server import context_server_via_uql

router = APIRouter(
    prefix="/profile",
    # dependencies=[Depends(get_current_user)]
)


@router.get("/{id}")
async def profile_get(id: str, uql=Depends(context_server_via_uql)):
    q = f"SELECT PROFILE WHERE id=\"{id}\""

    try:
        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        return result["list"][0]
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select")
async def select_profiles(request: Request, uql=Depends(context_server_via_uql)):
    try:
        q = await request.body()
        q = q.decode('utf-8')
        if q:
            q = f"SELECT PROFILE WHERE {q}"
        else:
            q = "SELECT PROFILE"
        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        result = list(filter_profile(result))
        return result
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
