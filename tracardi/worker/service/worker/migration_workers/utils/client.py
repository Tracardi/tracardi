from elasticsearch import Elasticsearch

from tracardi.worker.config import elasticsearch_config
from tracardi.worker.domain.storage_record import StorageRecords, StorageRecord, RecordMetadata
from typing import Optional
from elasticsearch.exceptions import NotFoundError


class ElasticClient:

    def __init__(self, hosts):
        config = elasticsearch_config.get_elasticsearch_config()
        if 'hosts' not in config:
            config['hosts'] = hosts
        self._client = Elasticsearch(**config)

    def __enter__(self) -> 'ElasticClient':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._client.close()

    def reindex(self, body: dict, wait_for_completion=False) -> dict:
        return self._client.reindex(body=body, wait_for_completion=wait_for_completion)

    def count(self, index: str) -> int:
        return self._client.count(index=index).get("count", 0)

    def load_records(self, index: str, start: int, size: int) -> StorageRecords:
        result = self._client.search(
            body={"query": {"match_all": {}}, "from": start, "size": size},
            index=index
        )
        return StorageRecords.build_from_elastic(result)

    def upsert(self, index: str, record: StorageRecord, script: str) -> dict:
        return self._client.update(index, record.get_meta_data().id, body={
            "scripted_upsert": True,
            "script": {
                "source": f"ctx._source = params.document;\n{script}",
                "params": {
                    "document": record
                }
            },
            "upsert": {}
        })

    def load(self, index: str, id: str) -> Optional[StorageRecord]:
        try:
            result = self._client.get(index, id)
            result = StorageRecord(result)
            result.set_meta_data(RecordMetadata(id=id, index=index))
            return result

        except NotFoundError:
            return None

    def get_task(self, task_id: str) -> Optional[dict]:
        try:
            return self._client.tasks.get(task_id=task_id, wait_for_completion=False)

        except NotFoundError:
            return None
