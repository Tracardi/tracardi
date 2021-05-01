import httpx
from fastapi import APIRouter
from fastapi import HTTPException, Depends
from ..uql.query.dispatcher import Host
from ..uql.query.mappers.action_mapper import action_mapper
from ..globals.authentication import get_current_user
from ..globals.context_server_host import get_context_server_host


router = APIRouter(
    prefix="/ref",
    dependencies=[Depends(get_current_user)]
)


@router.get("/context/{strategy}")
async def ref_callbacks(strategy: str, host: Host = Depends(get_context_server_host)):
    if strategy not in ["actions", "conditions"]:
        raise HTTPException(status_code=404, detail="Incorrect url")

    try:
        async with httpx.AsyncClient() as client:
            url = host.uri(f'cxs/definitions/{strategy}/')
            context_server_response = await client.get(str(url))
        return context_server_response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uql/{strategy}")
async def ref_callbacks(strategy: str):
    if strategy not in ["actions", "conditions"]:
        raise HTTPException(status_code=404, detail="Incorrect url")

    try:
        result = []
        for name, values in action_mapper.items():
            action = {
                "name": name,
                "metadata": values["metadata"]
            }
            result.append(action)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))