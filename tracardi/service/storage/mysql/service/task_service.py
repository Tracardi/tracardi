import logging

from tracardi.config import tracardi
from tracardi.domain.task import Task
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.task_mapping import map_to_task_table
from tracardi.service.storage.mysql.schema.table import TaskTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_and_mode_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class BackgroundTaskService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(TaskTable, search, limit, offset)

    async def load_by_id(self, background_task_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(TaskTable, primary_id=background_task_id)

    async def delete_by_id(self, background_task_id: str) -> str:
        return await self._delete_by_id(TaskTable, primary_id=background_task_id)


    async def update_by_id(self, background_task_id: str, data: dict) -> str:
        return await self._update_by_id(TaskTable, background_task_id, data)


    async def insert(self, background_task: Task):
        return await self._replace(TaskTable, map_to_task_table(background_task))


    async def load_all_by_type(self, wf_type: str, search: str = None, columns=None, limit: int = None, offset: int = None) -> SelectResult:
        if search:
            where = where_tenant_and_mode_context(
                TaskTable,
                TaskTable.type == wf_type,
                TaskTable.name.like(f'%{search}%')
            )
        else:
            where = where_tenant_and_mode_context(
                TaskTable,
                TaskTable.type == wf_type
            )

        return await self._select_query(TaskTable,
                                        columns=columns,
                                        where=where,
                                        order_by=TaskTable.timestamp.desc(),
                                        limit=limit,
                                        offset=offset,
                                        one_record=False)

