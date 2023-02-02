from worker.service.worker.migration_workers.utils.reindex_with_operation import reindex_with_operation
from worker.domain.migration_schema import MigrationSchema
from worker.service.worker.migration_workers.utils.client import ElasticClient
from worker.domain.storage_record import StorageRecord


@reindex_with_operation
def user_reindex(celery_job, schema: MigrationSchema, url: str, task_index: str, record: StorageRecord):
    with ElasticClient(hosts=[url]) as client:
        user = client.load(schema.copy_index.from_index, record.get_meta_data().id)
        user_exists = user is not None

        record = StorageRecord({key: record[key] for key in record if key != "token"})

        if user_exists:
            record["token"] = user["token"]
        else:
            record["token"] = None

        return record
