from sqlalchemy import desc
from uuid import uuid4

from typing import Optional, Tuple

from tracardi.domain.task import Task
from tracardi.common.logging.log_handler import get_logger
from tracardi.service.storage.mysql.mapping.task_mapping import map_to_task_table, map_to_task
from tracardi.service.storage.mysql.schema.table import TaskTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context
from tracardi.service.utils.date import now_in_utc

logger = get_logger(__name__)


class BackgroundTaskService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(TaskTable, search, limit, offset, order_by=desc(TaskTable.timestamp))

    async def load_by_id(self, background_task_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(TaskTable, primary_id=background_task_id)

    async def delete_by_id(self, background_task_id: str) -> Tuple[bool, Optional[Task]]:
        return await self._delete_by_id_in_deployment_mode(TaskTable, map_to_task,
                                                           primary_id=background_task_id)


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

        return await self._select_in_deployment_mode(
            TaskTable,
            columns=columns,
            where=where,
            order_by=TaskTable.timestamp.desc(),
            limit=limit,
            offset=offset,
            one_record=False)

    async def task_create(self, type: str, name: str, params=None) -> str:

        if params is None:
            params = {}
        try:

            task_id = str(uuid4())
            await self.insert(Task(
                id=task_id,
                name=name,
                timestamp=now_in_utc(),
                status="pending",
                progress=0,
                type=type,
                params=params,
                task_id=task_id
            ))
            logger.info(msg=f"Successfully added task name \"{name}\"")

            return task_id

        except Exception as e:
            logger.error(msg=f"Could not add task with name \"{name}\" due to an error: {str(e)}")

    async def task_progress(self, task_id: str, progress: int):

        try:

            await self.update_by_id(task_id, {
                "progress": progress,
                "status": "running"
            })

            logger.info(msg=f"Successfully updated task ID \"{task_id}\"")

            return task_id

        except Exception as e:
            logger.error(msg=f"Could not update task with ID \"{task_id}\" due to an error: {str(e)}")

    async def task_finish(self, task_id: str):
        try:

            await self.update_by_id(task_id, {
                "progress": 100,
                "status": "finished"
            })

            logger.info(msg=f"Successfully finished task ID \"{task_id}\"")

            return task_id

        except Exception as e:
            logger.error(msg=f"Could not finish task with ID \"{task_id}\" due to an error: {str(e)}")

    async def task_status(self, task_id: str, status, message: Optional[str] = None):
        try:

            bts = BackgroundTaskService()

            await bts.update_by_id(task_id, {
                "status": status,
                "message": message
            })

            logger.info(msg=f"Successfully changed status for task ID \"{task_id}\"")

            return task_id

        except Exception as e:
            logger.error(msg=f"Could not change status for task with ID \"{task_id}\" due to an error: {str(e)}")
