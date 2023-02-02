from worker.domain.migration_schema import MigrationSchema
from worker.service.worker.migration_workers.utils.reindex_with_operation import reindex_with_operation
from worker.misc.base_64 import b64_decoder, b64_encoder
from worker.domain.storage_record import StorageRecord


@reindex_with_operation
def validation_schema_reindex(celery_job, schema: MigrationSchema, url: str, task_index: str, record: StorageRecord):
    record["validation"] = b64_encoder({
        "json_schema": b64_decoder(record["validation"]),
        "enabled": record["enabled"]
    })

    return record
