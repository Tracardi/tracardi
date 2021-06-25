from fastapi import APIRouter
from fastapi import HTTPException, Depends

from .auth.authentication import get_current_user

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.post("/graphql/profile", tags=["graphql", "profile"])
async def profile_graph_ql():
    try:
        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
