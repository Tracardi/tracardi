from tracardi.context import Context, ServerContext
from tracardi.worker.domain.migration_schema import MigrationSchema
from tracardi.worker.misc.update_progress import update_progress
from tracardi.worker.misc.task_progress import task_create
from time import sleep
from tracardi.worker.service.worker.migration_workers.utils.migration_error import MigrationError
import logging
from tracardi.worker.service.worker.migration_workers.utils.client import ElasticClient


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
                    raise MigrationError(f"Import encountered failures: {response['failures']}")

            if schema.wait_for_completion is False:
                # Async processing
                if "task" not in response:
                    raise MigrationError("No task in reindex response.")

                task_id = response["task"]

                while True:
                    task_response = client.get_task(task_id)
                    if task_response is None:
                        break

                    if task_response["completed"] is True:
                        if 'error' in task_response:
                            error = f"Migration task {task_response['task']['node']}:{task_response['task']['id']} " \
                                    f"from `{schema.copy_index.from_index}` to `{schema.copy_index.to_index}` " \
                                    f"FAILED due to {task_response}. "
                            raise MigrationError(error)
                        break

                    status = task_response["task"]["status"]
                    # update_progress(celery_job, status["updated"] + status["created"], status["total"])
                    sleep(3)

                logging.info(f"Migration from `{schema.copy_index.from_index}` to `{schema.copy_index.to_index}` COMPLETED.")

                # update_progress(celery_job, 100)
