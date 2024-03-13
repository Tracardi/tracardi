import re

from datetime import datetime
from time import sleep
import logging

from tracardi.context import Context
from tracardi.worker.domain.migration_schema import MigrationSchema
from tracardi.worker.misc.task_progress import task_create, task_status
from tracardi.worker.service.worker.migration_workers.utils.migration_error import MigrationError
from tracardi.worker.service.worker.migration_workers.utils.client import ElasticClient


def _get_partitioning_suffix(partitioning) -> str:
    """
    Current date suffix
    """
    date = datetime.now()
    if partitioning == 'month':
        return f"{date.year}-{date.month}"
    elif partitioning == 'year':
        return f"{date.year}-year"
    elif partitioning == 'day':
        return f"{date.year}-{date.month}/{date.day}"
    elif partitioning == 'hour':
        return f"{date.year}-{date.month}/{date.day}/{date.hour}"
    elif partitioning == 'minute':
        return f"{date.year}-{date.month}/{date.day}/{date.hour}/{date.minute}"
    elif partitioning == 'quarter':
        return f"{date.year}-q{(date.month % 4) + 1}"
    else:
        raise ValueError("Unknown partitioning. Expected: year, month, quarter, or day")

async def reindex_to_one_index(schema: MigrationSchema, url: str, context: Context):

    if not 'replace' in schema.params and 'partitioning' not in schema.params:
        logging.info(f"Migration from `{schema.copy_index.from_index}` FAILED. Wrong configuration. "
                     f"Missing params.replace or params.partitioning.")
        return

    partition = _get_partitioning_suffix(schema.params['partitioning'])
    pattern = schema.params['replace']
    schema.copy_index.to_index = re.sub(pattern, partition, schema.copy_index.to_index)

    task_id = await task_create(
        "upgrade",
        f"Migration of \"{schema.copy_index.from_index}\" to \"{schema.copy_index.to_index}\"",
        schema.model_dump()
    )

    logging.info(f"Migrating to one `{schema.copy_index.to_index}` STARTED.")

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
        print(f"Reindexing with\n{body}")
        response = client.reindex(body=body, wait_for_completion=schema.wait_for_completion)
        print(f"Response:\n{response}")

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

                        await task_status(task_id, 'error', error)

                        raise MigrationError(error)
                    break

                status = task_response["task"]["status"]
                # update_progress(celery_job, status["updated"] + status["created"], status["total"])
                sleep(3)

            logging.info(f"Migration from `{schema.copy_index.from_index}` to `{schema.copy_index.to_index}` COMPLETED.")

            # update_progress(celery_job, 100)
