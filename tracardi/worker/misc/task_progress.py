from uuid import uuid4

from tracardi.domain.task import Task
from tracardi.service.storage.mysql.mapping.task_mapping import map_to_task
from tracardi.service.storage.mysql.service.task_service import BackgroundTaskService
from tracardi.service.utils.date import now_in_utc
import logging


logger = logging.getLogger(__name__)


async def task_load(task_id: str) -> Task:

    try:

        bts = BackgroundTaskService()
        record = await bts.load_by_id(task_id)
        return record.map_to_object(map_to_task)

    except Exception as e:
        logger.error(msg=f"Could not add task with ID \"{task_id}\" due to an error: {str(e)}")



async def task_create(type: str, name: str, params=None):

    if params is None:
        params = {}
    try:

        bts = BackgroundTaskService()
        task_id = str(uuid4())
        await bts.insert(Task(
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

async def task_progress(task_id: str, progress: int):

    try:

        bts = BackgroundTaskService()

        await bts.update_by_id(task_id, {
            "progress": progress
        })

        logger.info(msg=f"Successfully updated task ID \"{task_id}\"")

        return task_id

    except Exception as e:
        logger.error(msg=f"Could not add task with ID \"{task_id}\" due to an error: {str(e)}")


async def task_finish(task_id: str):
    await task_progress(task_id, 100)


