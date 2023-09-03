from tracardi.worker.domain.migration_schema import MigrationSchema
from tracardi.worker.misc.update_progress import update_progress
from tracardi.worker.misc.add_task import add_task
from tracardi.worker.service.worker.migration_workers.utils.migration_error import MigrationError
import functools
from .client import ElasticClient


def reindex_with_operation(func):
    @functools.wraps(func)
    def wrapper(celery_job, schema: MigrationSchema, url: str, task_index: str):
        add_task(
            url,
            task_index,
            f"Migration of \"{schema.copy_index.from_index}\"",
            celery_job,
            schema.model_dict()
        )

        def transform_func(data):
            return func(celery_job, schema, url, task_index, data)

        try:
            with ElasticClient(hosts=[url]) as client:
                update_progress(celery_job, 0, doc_count := client.count(schema.copy_index.from_index))
                pagesize = 10
                moved_records = 0

                if schema.copy_index.script is None:
                    schema.copy_index.script = ""

                while records_to_move := client.load_records(
                        index=schema.copy_index.from_index,
                        start=moved_records,
                        size=pagesize
                ):

                    records_to_move.transform_hits(transform_func)

                    for number, record in enumerate(records_to_move):
                        client.upsert(
                            index=schema.copy_index.to_index,
                            record=record,
                            script=schema.copy_index.script
                        )

                        update_progress(celery_job, moved_records + number + 1, doc_count)

                    moved_records += pagesize

        except Exception as e:
            raise MigrationError(f"Index {schema.copy_index.from_index} could not be moved due to an error: {str(e)}")

    return wrapper
