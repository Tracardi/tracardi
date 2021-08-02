import asyncio
import hashlib
from collections import defaultdict
from time import sleep
from typing import Optional

from fastapi import APIRouter
from fastapi import HTTPException, Depends
from tracardi_graph_runner.domain.flow_history import FlowHistory
from tracardi_graph_runner.domain.work_flow import WorkFlow

from .auth.authentication import get_current_user
from .grouper import search
from ..domain.context import Context
from ..domain.enum.yes_no import YesNo
from ..domain.flow_meta_data import FlowMetaData
from ..domain.entity import Entity
from ..domain.event import Event
from ..domain.flow import Flow, FlowGraphDataRecord
from tracardi_graph_runner.domain.flow import Flow as GraphFlow
from ..domain.flow_action_plugin import FlowActionPlugin
from ..domain.plugin_import import PluginImport
from ..domain.record.flow_action_plugin_record import FlowActionPluginRecord
from ..domain.flow_action_plugins import FlowActionPlugins
from ..domain.flow import FlowRecord
from ..domain.flows import Flows

from ..domain.profile import Profile
from ..domain.rule import Rule
from ..domain.session import Session
from ..domain.settings import Settings
from ..domain.source import Source
from ..domain.value_object.bulk_insert_result import BulkInsertResult
from ..event_server.service.persistence_service import PersistenceService

from ..service.storage.crud import EntityStorageCrud
from ..service.storage.elastic_storage import ElasticStorage
from ..setup.on_start import add_plugin

router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.post("/flow/draft", tags=["flow"], response_model=BulkInsertResult)
async def upsert_flow_draft(draft: Flow):
    sleep(1)
    try:

        # Check if origin flow exists

        entity = Entity(id=draft.id)
        draft_record = await entity.storage('flow').load(FlowRecord)  # type: FlowRecord

        if draft_record is None:
            # If not exists create new one
            origin = Flow.new(draft.id)
            origin.description = "Created during workflow draft save."
            record = FlowRecord.encode(origin)
            await record.storage().save()
        else:
            # If exists decode origin flow
            origin = draft_record.decode()

        # Append draft
        origin.encode_draft(draft)
        flow_record = FlowRecord.encode(origin)
        return await flow_record.storage().save()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/draft/{id}", tags=["flow"], response_model=Flow)
async def load_flow_draft(id: str):
    sleep(1)
    try:

        # Check if origin flow exists

        entity = Entity(id=id)
        draft_record = await entity.storage('flow').load(FlowRecord)  # type: FlowRecord

        if draft_record is None:
            raise ValueError("Flow `{}` does not exists.".format(id))

        # Return draft if exists
        if draft_record.draft:
            return draft_record.decode_draft()

        return draft_record.decode()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flows", tags=["flow"])
async def get_flows(query: str = None):
    try:
        flows = Flows()
        result = await flows.bulk().load()
        total = result.total
        result = [FlowRecord(**r) for r in result]

        # Filtering
        if query is not None and len(query) > 0:
            query = query.lower()
            if query:
                result = [r for r in result if query in r.name.lower() or search(query, r.projects)]

        return {
            "total": total,
            "result": result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flows/by_tag", tags=["flow"])
async def get_grouped_flows(query: str = None):
    sleep(1)
    try:
        flows = Flows()
        result = await flows.bulk().load()
        total = result.total
        result = [FlowRecord(**r) for r in result]

        # Filtering
        if query is not None and len(query) > 0:
            query = query.lower()
            if query:
                result = [r for r in result if query in r.name.lower() or search(query, r.projects)]

        # Grouping
        groups = defaultdict(list)
        for flow in result:  # type: FlowRecord
            if isinstance(flow.projects, list):
                for group in flow.projects:
                    groups[group].append(flow)
            elif isinstance(flow.projects, str):
                groups[flow.projects].append(flow)

        # Sort
        groups = {k: sorted(v, key=lambda r: r.name, reverse=False) for k, v in groups.items()}

        return {
            "total": total,
            "grouped": groups
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/flow/{id}", tags=["flow"], response_model=dict)
async def delete_flow(id: str):
    try:
        # delete rule before flow

        crud = EntityStorageCrud('rule', Rule)
        rule_delete_task = asyncio.create_task(crud.delete_by('flow.id.keyword', id))

        flow = Entity(id=id)
        flow_delete_task = asyncio.create_task(flow.storage("flow").delete())

        return {
            "rule": await rule_delete_task,
            "flow": await flow_delete_task
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/{id}", tags=["flow"], response_model=Flow)
async def get_flow(id: str):
    try:
        rule = Entity(id=id)
        flow_record = await rule.storage("flow").load(FlowRecord)
        if flow_record is None:
            raise ValueError("Flow does not exist.")
        result = flow_record.decode()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flow", tags=["flow"], response_model=BulkInsertResult)
async def upsert_flow(flow: Flow):
    try:
        flow_record = FlowRecord.encode(flow)
        return await flow_record.storage().save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flow/metadata", tags=["flow"], response_model=BulkInsertResult)
async def upsert_flow_details(flow_metadata: FlowMetaData):
    sleep(1)
    try:
        entity = Entity(id=flow_metadata.id)
        flow_record = await entity.storage("flow").load(FlowRecord)  # type: FlowRecord
        if flow_record:
            flow_record.name = flow_metadata.name
            flow_record.description = flow_metadata.description
            flow_record.enabled = flow_metadata.enabled
            flow_record.projects = flow_metadata.projects
        else:
            # new record
            flow_record = FlowRecord(
                id=flow_metadata.id,
                name=flow_metadata.name,
                description=flow_metadata.description,
                enabled=flow_metadata.enabled,
                flowGraph=FlowGraphDataRecord(nodes=[], edges=[]),
                projects=flow_metadata.projects
            )

        return await flow_record.storage().save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/metadata/refresh", tags=["flow"])
async def flow_refresh():
    service = PersistenceService(ElasticStorage(index_key='flow'))
    return await service.refresh()


@router.get("/flow/metadata/flush", tags=["flow"])
async def flow_refresh():
    service = PersistenceService(ElasticStorage(index_key='flow'))
    return await service.flush()


@router.post("/flow/draft/metadata", tags=["flow"], response_model=BulkInsertResult)
async def upsert_flow_details(flow_metadata: FlowMetaData):
    try:
        entity = Entity(id=flow_metadata.id)
        flow_record = await entity.storage("flow").load(FlowRecord)  # type: FlowRecord

        if flow_record is None:
            raise ValueError("Flow `{}` does not exist.".format(flow_metadata.id))

        draft = flow_record.decode_draft()

        draft.name = flow_metadata.name
        draft.description = flow_metadata.description
        draft.enabled = flow_metadata.enabled
        draft.projects = flow_metadata.projects

        flow_record.encode_draft(draft)
        return await flow_record.storage().save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/{id}/lock/{lock}", tags=["flow"], response_model=BulkInsertResult)
async def upsert_flow_details(id: str, lock: str):
    try:
        entity = Entity(id=id)
        flow_record = await entity.storage("flow").load(FlowRecord)  # type: FlowRecord

        if flow_record is None:
            raise ValueError("Flow `{}` does not exist.".format(id))

        flow_record.lock = True if lock.lower() == 'yes' else False
        return await flow_record.storage().save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flow/debug", tags=["flow"])
async def debug_flow(flow: GraphFlow):
    """
        Debugs flow sent in request body
    """
    try:

        profile = Profile(id="@debug-profile-id")
        session = Session(id="@debug-session-id")
        session.operation.new = True
        event = Event(
            id='@debug-event-id',
            type="@debug-event-type",
            source=Source(id="@debug-source-id", type="web-page"),
            session=session,
            profile=profile,
            context=Context()
        )

        workflow = WorkFlow(
            FlowHistory(history=[]),
            session,
            profile,
            event
        )
        debug_info = await workflow.invoke(flow, debug=True)

        if profile.operation.needs_update():
            profile_save_result = await profile.storage().save()
        else:
            profile_save_result = None

        return {
            "debugInfo": debug_info.dict(),
            "update": profile_save_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/flow/{id}/debug", tags=["flow"])
# async def debug_flow_by_id(id: str):
#
#     """
#     Debugs flow by reading it from storage
#     """
#
#     sleep(1)
#     # Load flow
#     try:
#         profile = Profile(id="@debug-profile-id")
#         session = Session(id="@debug-session-id")
#         session.operation.new = True
#         event = Event(
#             id='@debug-event-id',
#             type="@debug-event-type",
#             source=Source(id="@debug-source-id", type="web-page"),
#             session=session,
#             profile=profile,
#             context=Context()
#         )
#
#         flow_record_entity = Entity(id=id)
#         flow_record = await flow_record_entity.storage("flow").load(FlowRecord)  # type: FlowRecord
#         flow = flow_record.decode_draft()
#
#         workflow = WorkFlow(
#             FlowHistory(history=[]),
#             session,
#             profile,
#             event
#         )
#         debug_info = await workflow.invoke(flow, debug=True)
#
#         if profile.operation.needs_update():
#             profile_save_result = await profile.storage().save()
#         else:
#             profile_save_result = None
#
#         debug_info_by_id = defaultdict(list)
#         for info in debug_info.calls:
#             debug_info_by_id[info.node.id].append(info)
#
#         return {
#             "calls": debug_info_by_id,
#             "update": profile_save_result
#         }
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/action/plugin/{id}", tags=["flow", "action", "plugin"], response_model=FlowActionPlugin)
async def get_plugin(id: str):
    """
    Returns FlowActionPlugin object.
    """
    try:
        action = Entity(id=id)
        record = await action.storage("action").load(FlowActionPluginRecord)  # type: FlowActionPluginRecord
        return record.decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/action/plugin/{id}/hide/{state}", tags=["flow", "action", "plugin"], response_model=BulkInsertResult)
async def get_plugin_state(id: str, state: YesNo):
    """
    Returns FlowActionPlugin object.
    """

    try:

        action = Entity(id=id)
        record = await action.storage("action").load(FlowActionPluginRecord)  # type: FlowActionPluginRecord
        action = record.decode()
        action.settings.hidden = Settings.as_bool(state)
        return await FlowActionPluginRecord.encode(action).storage().save()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/action/plugin/{id}/enable/{state}", tags=["flow", "action", "plugin"],
            response_model=BulkInsertResult)
async def get_plugin_enabled(id: str, state: YesNo):
    """
    Returns FlowActionPlugin object.
    """

    try:

        action = Entity(id=id)
        record = await action.storage("action").load(FlowActionPluginRecord)  # type: FlowActionPluginRecord
        action = record.decode()
        action.settings.enabled = Settings.as_bool(state)
        return await FlowActionPluginRecord.encode(action).storage().save()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/action/plugin/{id}", tags=["flow", "action", "plugin"], response_model=FlowActionPlugin)
async def get_plugin(id: str):
    """
    Returns FlowActionPlugin object.
    """
    try:
        action = Entity(id=id)
        record = await action.storage("action").load(FlowActionPluginRecord)  # type: FlowActionPluginRecord
        return record.decode()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/flow/action/plugin/{id}", tags=["flow", "action", "plugin"], response_model=dict)
async def delete_plugin(id: str):
    """
    Deletes FlowActionPlugin object.
    """
    try:
        action = Entity(id=id)
        return await action.storage("action").delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flow/action/plugin", tags=["flow", "action", "plugin"], response_model=BulkInsertResult)
async def upsert_plugin(action: FlowActionPlugin):
    """
    Upserts workflow action plugin. Action plugin id is a hash of its module and className so
    if there is a conflict in classes or you pass wrong mdoule and class name then the action
    plugin may be overwritten.
    """

    try:
        action_id = action.plugin.spec.module + action.plugin.spec.className
        action.id = hashlib.md5(action_id.encode()).hexdigest()

        record = FlowActionPluginRecord.encode(action)

        return await record.storage().save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flow/action/plugins", tags=["flow", "action", "plugin"])
async def get_plugins_list(query: Optional[str] = None):
    """
    Returns a list of available plugins.
    """

    try:

        plugins = FlowActionPlugins()
        result = await plugins.bulk().load()
        _result = [FlowActionPluginRecord(**r).decode() for r in result]

        if query is not None and len(query) > 0:
            query = query.lower()

            if query == "*not-hidden":
                _result = [r for r in _result if r.settings.hidden is False]
            if query == "*hidden":
                _result = [r for r in _result if r.settings.hidden is True]
            if query == "*enabled":
                _result = [r for r in _result if r.settings.enabled is True]
            if query == "*disabled":
                _result = [r for r in _result if r.settings.enabled is False]
            if query[0] != '*':
                _result = [r for r in _result if
                           query in r.plugin.metadata.name.lower() or search(query, r.plugin.metadata.group)]

        groups = defaultdict(list)
        for plugin in _result:  # type: FlowActionPlugin
            if isinstance(plugin.plugin.metadata.group, list):
                for group in plugin.plugin.metadata.group:
                    groups[group].append(plugin)
            elif isinstance(plugin.plugin.metadata.group, str):
                groups[plugin.plugin.metadata.group].append(plugin)

        # Sort
        groups = {k: sorted(v, key=lambda r: r.plugin.metadata.name, reverse=False) for k, v in groups.items()}

        return {
            "total": result.total,
            "grouped": groups
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flow/action/plugin/register", tags=["flow", "action", "plugin"], response_model=BulkInsertResult)
async def register_plugin_by_module(plugin: PluginImport):
    """
    Registers action plugin by its module. Module must have register method that returns Plugin
    class filled with plugin metadata.
    """

    try:
        result = await add_plugin(plugin.module, upgrade=plugin.upgrade)
        service = PersistenceService(ElasticStorage(index_key='action'))
        await service.refresh()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
