from tracardi.domain.migration_schema import MigrationSchema
from typing import Optional, List, Tuple
import hashlib
import json
from tracardi.service.storage.elastic_client import ElasticClient
from worker.celery_worker import run_migration_job
import asyncio
from concurrent.futures import ThreadPoolExecutor
from tracardi.domain.task import Task
from datetime import datetime
from uuid import uuid4
from tracardi.service.storage.driver import storage
from pathlib import Path


class MigrationNotFoundException(Exception):
    pass


class MigrationManager:
    available_migrations = {
        ("070", "071"): "test"
    }

    def __init__(self, from_version: str, to_version: str, from_prefix: Optional[str] = None,
                 to_prefix: Optional[str] = None):
        self.from_version = from_version.replace(".", "")
        self.to_version = to_version.replace(".", "")
        self.from_prefix = from_prefix if from_prefix is not None else \
            hashlib.md5(from_version.encode('utf-8')).hexdigest()[:5]
        self.to_prefix = to_prefix if to_prefix is not None else \
            hashlib.md5(to_version.encode('utf-8')).hexdigest()[:5]

    def get_schemas(self):
        try:
            filename = self.available_migrations[(self.from_version, self.to_version)]

        except KeyError:
            raise MigrationNotFoundException(f"Migration from {self.from_version} to {self.to_version} not found.")

        with open(
            f"{Path(__file__).parent}/schemas/{filename}.json",
            mode="r"
        ) as f:
            return [MigrationSchema(**schema) for schema in json.load(f)]

    async def start_migration(self, ids: List[str], elastic_host: str) -> Tuple[str, str]:

        schemas = [schema for schema in self.get_schemas() if schema.id in ids]

        final_schemas = []
        for schema in schemas:
            if schema.multi is True:
                es = ElasticClient.instance()
                from_indices = [index for index in await es.list_indices() if index.startswith(
                    f"{self.from_version}.{self.from_prefix}.{schema.name}"
                )]
                for from_index in from_indices:
                    final_schemas.append(MigrationSchema(
                        id=str(uuid4()),
                        name=from_index.split('.')[-1],
                        multi=schema.multi,
                        asynchronous=schema.asynchronous,
                        script=schema.script,
                        worker=schema.worker,
                        from_index=from_index,
                        to_index=f"{self.to_version}.{self.to_prefix}.{from_index.split('.')[-1]}"
                    ))

            else:
                schema.from_index = f"{self.from_version}.{self.from_prefix}.{schema.name}"
                schema.to_index = f"{self.to_version}.{self.to_prefix}.{schema.name}"
                final_schemas.append(schema)

        final_schemas = [schema.dict() for schema in final_schemas]

        def add_to_celery(given_schemas: List, elastic: str):
            return run_migration_job.delay(given_schemas, elastic)

        executor = ThreadPoolExecutor(
            max_workers=1,
        )
        loop = asyncio.get_running_loop()
        blocking_tasks = [loop.run_in_executor(executor, add_to_celery, final_schemas, elastic_host)]
        completed, pending = await asyncio.wait(blocking_tasks)
        celery_task = completed.pop().result()

        task = Task(
            timestamp=datetime.utcnow(),
            id=str(uuid4()),
            name=f"{self.from_version}.{self.from_prefix} to {self.to_version}.{self.to_prefix} migration",
            import_type="migration",
            event_type="<no-event-type>",
            import_id=final_schemas[0]["id"],
            task_id=celery_task.id
        )

        await storage.driver.task.upsert_task(task)

        return task.id, celery_task.id
