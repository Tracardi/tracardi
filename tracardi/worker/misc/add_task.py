from worker.service.worker.migration_workers.utils.client import ElasticClient
from datetime import datetime
import logging
from worker.domain.storage_record import StorageRecord, RecordMetadata


logger = logging.getLogger(__name__)


def add_task(elastic_host: str, task_index: str, name: str, job, params=None):

    if params is None:
        params = {}
    try:
        with ElasticClient(hosts=[elastic_host]) as client:
            task = StorageRecord({
                    "id": job.request.id,
                    "name": name,
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
                    "status": "PROGRESS",
                    "type": "upgrade",
                    "progress": 0.,
                    "event_type": "missing",
                    "params": params,
                    "task_id": job.request.id
            })
            task.set_meta_data(RecordMetadata(id=task["id"], index=task_index))
            client.upsert(task_index, task, "")
            logger.info(msg=f"Successfully added task with ID {job.request.id}")

    except Exception as e:
        logger.info(msg=f"Could not add task with ID {job.request.id} due to an error: {str(e)}")

