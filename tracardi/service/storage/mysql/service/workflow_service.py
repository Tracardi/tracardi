import logging
from typing import Optional, Tuple

from tracardi.config import tracardi
from tracardi.domain.flow import FlowRecord
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.workflow_mapping import map_to_workflow_table, map_to_workflow_record
from tracardi.service.storage.mysql.schema.table import WorkflowTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class WorkflowService(TableService):

    async def load_in_current_context(self, workflow_id):
        return await self._load_by_id(WorkflowTable, primary_id=workflow_id)

    async def load_all(self, search: str = None, columns=None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(WorkflowTable, search, limit, offset, columns)

    async def load_by_id(self, workflow_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(WorkflowTable, primary_id=workflow_id)

    async def update_by_id(self, workflow_id: str, new_data: dict) -> Optional[str]:
        return await self._update_by_id(WorkflowTable, primary_id=workflow_id, new_data=new_data)

    async def delete_by_id(self, workflow_id: str) -> Tuple[bool, Optional[FlowRecord]]:
        return await self._delete_by_id_in_deployment_mode(WorkflowTable,
                                                           map_to_workflow_record,
                                                           primary_id=workflow_id)

    async def insert(self, workflow: FlowRecord):
        return await self._replace(WorkflowTable, map_to_workflow_table(workflow))

    async def load_all_by_type(self, wf_type: str, search: str = None, columns=None, limit: int = None,
                               offset: int = None) -> SelectResult:
        if search:
            where = where_tenant_and_mode_context(
                WorkflowTable,
                WorkflowTable.type == wf_type,
                WorkflowTable.name.like(f'%{search}%')
            )
        else:
            where = where_tenant_and_mode_context(
                WorkflowTable,
                WorkflowTable.type == wf_type
            )

        return await self._select_in_deployment_mode(WorkflowTable,
                                                     columns=columns,
                                                     where=where,
                                                     order_by=WorkflowTable.name,
                                                     limit=limit,
                                                     offset=offset,
                                                     one_record=False)
