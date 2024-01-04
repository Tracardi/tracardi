from tracardi.config import tracardi
from tracardi.context import Context, ServerContext
from tracardi.exceptions.log_handler import log_handler
from tracardi.worker.domain.migration_schema import MigrationSchema
from tracardi.worker.misc.task_progress import task_create, task_status, task_finish, task_progress
from time import sleep
from tracardi.worker.service.worker.migration_workers.utils.migration_error import MigrationError
import logging
from tracardi.worker.service.worker.migration_workers.utils.client import ElasticClient

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def reindex(schema: MigrationSchema, url: str, context: Context):
    with ServerContext(context):
        task_id = await task_create(
            "upgrade",
            f"Migration of \"{schema.copy_index.from_index}\"",
            schema.model_dump()
        )

        body = {
            "source": {
                "index": schema.copy_index.from_index
            },
            "dest": {
                "index": schema.copy_index.to_index
            }
        }

        if schema.copy_index.script is not None:
            body["script"] = {"lang": "painless", "source": schema.copy_index.script}

        with ElasticClient(hosts=[url]) as client:

            response = client.reindex(body=body, wait_for_completion=schema.wait_for_completion)

            if not isinstance(response, dict):
                raise MigrationError(str(response))

            if schema.wait_for_completion is True:

                if 'failures' in response and len(response['failures']) > 0:
                    error_message = f"Import encountered failures: {response['failures']}"
                    await task_status(task_id, "error", error_message)
                    raise MigrationError(error_message)

            if schema.wait_for_completion is False:
                # Async processing
                if "task" not in response:
                    error_message = "No task in reindex response."
                    await task_status(task_id, "error", error_message)
                    raise MigrationError(error_message)

                es_task_id = response["task"]

                while True:
                    task_response = client.get_task(es_task_id)
                    if task_response is None:
                        break

                    if task_response["completed"] is True:
                        if 'error' in task_response:
                            error = f"Migration task {task_response['task']['node']}:{task_response['task']['id']} " \
                                    f"from `{schema.copy_index.from_index}` to `{schema.copy_index.to_index}` " \
                                    f"FAILED due to {task_response}. "

                            await task_status(task_id, 'error', error)
                            logger.error(error)
                            raise MigrationError(error)
                        break

                    status = task_response["task"]["status"]

                    if status["total"] == 0:
                        progress = 0
                    else:
                        progress = int(((status["updated"] + status["created"]) / status["total"]) * 100)

                    await task_progress(task_id, progress)
                    sleep(3)

                logger.info(f"Migration from `{schema.copy_index.from_index}` to `{schema.copy_index.to_index}` COMPLETED.")

                await task_finish(task_id)
