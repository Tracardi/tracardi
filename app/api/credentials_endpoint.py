from collections import defaultdict

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from .auth.authentication import get_current_user
from .grouper import search
from ..domain.credential import CredentialRecords, Credential, CredentialRecord
from ..domain.project import Project, Projects
from ..domain.entity import Entity
from ..domain.value_object.bulk_insert_result import BulkInsertResult

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.get("/credentials/by_type", tags=["credential"])
async def get_credentials(query: str = None):
    try:
        credentials = CredentialRecords()
        result = await credentials.bulk().load()
        total = result.total
        result = CredentialRecords.decode(result)

        # Filtering
        if query is not None and len(query) > 0:
            query = query.lower()
            if query:
                result = [r for r in result if query in r.name.lower() or search(query, r.type)]

        # Grouping
        groups = defaultdict(list)
        for credential in result:  # type: Credential
            if isinstance(credential.group, list):
                for group in credential.group:
                    groups[group].append(credential)
            elif isinstance(credential.group, str):
                groups[credential.group].append(credential)

        # Sort
        groups = {k: sorted(v, key=lambda r: r.name, reverse=False) for k, v in groups.items()}

        return {
            "total": total,
            "grouped": groups
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/credential/{id}", tags=["credential"], response_model=Project)
async def get_credential_by_id(id: str):
    try:
        credential = Entity(id=id)
        record = await credential.storage('credential').load()  # type: CredentialRecord
        credential = record.decode()
        return credential
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credential", tags=["credential"], response_model=BulkInsertResult)
async def add_credential(credential: Credential):
    try:
        record = CredentialRecord.encode(credential)
        return await record.storage().save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/credential/{id}", tags=["credential"], response_model=dict)
async def delete_project(id: str):
    try:
        credential = Entity(id=id)
        return await credential.storage('credential').delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
