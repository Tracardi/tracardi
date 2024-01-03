from tracardi.domain.task import Task
from tracardi.service.storage.mysql.service.task_service import BackgroundTaskService
from tracardi.service.utils.date import now_in_utc
import logging


logger = logging.getLogger(__name__)


async def add_task(name: str, job, params=None):

    if params is None:
        params = {}

    bts = BackgroundTaskService()
    await bts.insert(Task(
        id=job.request.id,
        name=name,
        timestamp=now_in_utc(),
        status="pending",
        progress=0,
        type="upgrade",
        params=params,
        task_id=job.request.id
    ))
    logger.info(msg=f"Successfully added task name \"{name}\"")

    # except Exception as e:
    #     logger.error(msg=f"Could not add task with name \"{name}\" due to an error: {str(e)}")

