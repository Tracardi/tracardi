import asyncio
from typing import List

from fastapi import APIRouter
from fastapi import HTTPException, Depends

from .auth.authentication import get_current_user
from ..domain.entity import Entity
from ..domain.flow import Flow
from ..domain.named_entity import NamedEntity
from ..domain.rule import Rule
from ..event_server.service.persistence_service import PersistenceService
from ..service.storage.elastic_storage import ElasticStorage

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.get("/rule/{id}", tags=["rule"], response_model=Rule)
async def get_rule(id: str):
    """
    Returns rule or None if rule does not exist.
    """

    try:
        rule = Entity(id=id)
        return await rule.storage("rule").load(Rule)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rule", tags=["rule"])
async def upsert_rule(rule: Rule):
    try:
        entity = Entity(id=rule.flow.id)
        flow = await entity.storage("rule").load(Flow)  # type: Flow
        add_flow_task = None
        if not flow:
            new_flow = NamedEntity(id=rule.flow.id, name=rule.flow.name)
            add_flow_task = asyncio.create_task(entity.storage("flow").save(new_flow.dict()))

        add_rule_task = asyncio.create_task(rule.storage().save())

        if add_flow_task:
            await add_flow_task
        return await add_rule_task

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rule/{id}", tags=["rule"])
async def delete_rule(id: str):
    try:
        rule = Entity(id=id)
        return await rule.storage("rule").delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules/by_flow/{id}", tags=["rules"], response_model=List[Rule])
async def get_rules_attached_to_flow(id: str):
    try:
        rules = PersistenceService(ElasticStorage(index_key='rule'))

        rules_attached_to_flow = await rules.load_by('flow.id.keyword', id)
        rules = [Rule(**rule) for rule in rules_attached_to_flow]
        return rules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules/refresh", tags=["rules"])
async def refresh_rules():
    service = PersistenceService(ElasticStorage(index_key='rule'))
    return await service.refresh()
