import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Tuple
from uuid import uuid4

from elasticsearch import AsyncElasticsearch

from tracardi.domain.import_config import ImportConfig
from tracardi.domain.task import Task
from tracardi.process_engine.action.v1.connectors.elasticsearch.query.model.config import ElasticCredentials
from .importer import Importer
from pydantic import BaseModel
from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from worker.celery_worker import run_elastic_import_job


class ElasticIndexImportConfig(BaseModel):
    source: NamedEntity
    index: NamedEntity
    batch: int


class ElasticSourceConfig(BaseModel):
    source: NamedEntity


class Endpoint(PluginEndpoint):

    @staticmethod
    async def fetch_indices(config: dict):
        config = ElasticSourceConfig(**config)
        resource = await storage.driver.resource.load(config.source.id)
        credentials = ElasticCredentials(**resource.credentials.production)

        if credentials.has_credentials():
            client = AsyncElasticsearch(
                [credentials.url],
                http_auth=(credentials.username, credentials.password),
                scheme=credentials.scheme,
                port=credentials.port
            )
        else:
            client = AsyncElasticsearch(
                [credentials.url],
                scheme=credentials.scheme,
                port=credentials.port
            )

        indices = await client.indices.get("*")
        indices = indices.keys()

        return {
            "total": len(indices),
            "result": [{"name": record, "id": record} for record in indices]
        }


class ElasticIndexImporter(Importer):
    config_model = ElasticIndexImportConfig

    init = {
        "source": {"name": "", "id": ""},
        "index": {"name": "", "id": ""},
        "batch": 100,
    }

    form = Form(groups=[FormGroup(
        fields=[
            FormField(
                name="Elastic resource",
                id="source",
                description="Select Elasticsearch resource you want to connect to. Resource must have database credentials defined.",
                component=FormComponent(type="resource", props={"tag": "elastic"})
            ),
            FormField(
                name="Index name",
                id="index",
                description="Select index that you want to fetch data from.",
                component=FormComponent(type="autocomplete", props={
                    "label": "Index",
                    "endpoint": {
                        "url": Endpoint.url(__name__, "fetch_indices"),
                        "method": "post"
                    }
                })
            ),
            FormField(
                name="Batch",
                id="batch",
                description="System will not import the whole data at once. It will break the whole data set into small batches. "
                            "Type a number of records that will be processed in one batch.",
                component=FormComponent(type="text", props={"label": "Batch"})
            )
        ])])

    async def run(self, task_name, import_config: ImportConfig) -> Tuple[str, str]:
        def add_to_celery(import_config, credentials):
            return run_elastic_import_job.delay(
                import_config.dict(),
                credentials
            )

        config = ElasticIndexImportConfig(**import_config.config)
        resource = await storage.driver.resource.load(config.source.id)
        credentials = resource.credentials.test if self.debug is True else resource.credentials.production

        # Adding to celery is blocking,run in executor
        executor = ThreadPoolExecutor(
            max_workers=1,
        )
        loop = asyncio.get_running_loop()
        blocking_tasks = [loop.run_in_executor(executor, add_to_celery, import_config, credentials)]
        completed, pending = await asyncio.wait(blocking_tasks)
        celery_task = completed.pop().result()

        # Save task

        task = Task(
            timestamp=datetime.utcnow(),
            id=str(uuid4()),
            name=task_name if task_name else import_config.name,
            import_type=import_config.name,
            event_type=import_config.event_type,
            import_id=import_config.id,
            task_id=celery_task.id
        )

        await storage.driver.task.upsert_task(task)

        return task.id, celery_task.id
