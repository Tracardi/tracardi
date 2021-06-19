from fastapi import APIRouter
from fastapi import HTTPException, Depends
from .auth.authentication import get_current_user
from ..domain.project import Project, Projects
from ..domain.entity import Entity
from ..domain.value_object.bulk_insert_result import BulkInsertResult

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.get("/projects", tags=["project"])
async def get_projects(query: str = None):
    try:
        projects = Projects()
        result = await projects.bulk().load()
        return list(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{id}", tags=["project"], response_model=Project)
async def get_project_by_id(id: str):
    try:
        project = Entity(id=id)
        return await project.storage('project').load()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/project", tags=["project"], response_model=BulkInsertResult)
async def add_project(project: Project):
    try:
        return await project.storage().save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/project/{id}", tags=["project"], response_model=dict)
async def delete_project(id: str):
    try:
        project = Entity(id=id)
        return await project.storage('project').delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
