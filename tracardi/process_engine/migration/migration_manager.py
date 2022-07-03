from tracardi.domain.migration_schema import MigrationSchema, CopyIndex
from typing import Optional, List
import json
from tracardi.service.storage.elastic_client import ElasticClient
from worker.celery_worker import run_migration_job
import asyncio
from concurrent.futures import ThreadPoolExecutor
from tracardi.domain.task import Task
from datetime import datetime
from hashlib import sha1
from tracardi.service.storage.driver import storage
from pathlib import Path
from tracardi.domain.version import Version


class MigrationNotFoundException(Exception):
    pass


class MigrationManager:
    available_migrations = {
        ("070", "071"): "test"
    }

    def __init__(self, from_version: str, to_version: str, from_prefix: Optional[str] = None,
                 to_prefix: Optional[str] = None):
        self.from_version = Version(version=from_version, name=from_prefix)
        self.to_version = Version(version=to_version, name=to_prefix)

    def get_schemas(self):
        try:
            filename = self.available_migrations[
                (self.from_version.get_version_prefix(), self.to_version.get_version_prefix())
            ]

        except KeyError:
            raise MigrationNotFoundException(
                f"Migration from {self.from_version.get_version_prefix()} to {self.to_version.get_version_prefix()} "
                f"not found."
            )

        with open(
                f"{Path(__file__).parent}/schemas/{filename}.json",
                mode="r"
        ) as f:
            return [MigrationSchema(**schema) for schema in json.load(f) if isinstance(schema, dict)]  # avoid comments

    async def get_multi_indices(self, template_name):
        es = ElasticClient.instance()
        return [index for index in await es.list_indices() if index.startswith(
            f"{self.from_version.get_version_prefix()}.{self.from_version.name}.{template_name}"
        )]

    async def start_migration(self, ids: List[str], elastic_host: str) -> None:

        schemas = [schema for schema in self.get_schemas() if schema.id in ids]

        final_schemas = []
        for schema in schemas:
            if schema.copy_index.multi is True:
                from_indices = await self.get_multi_indices(template_name=schema.copy_index.from_index)
                for from_index in from_indices:
                    final_schemas.append(MigrationSchema(
                        id=sha1(from_index.encode("utf-8")).hexdigest(),
                        copy_index=CopyIndex(
                            from_index=from_index,
                            to_index=f"{self.to_version.get_version_prefix()}.{self.to_version.name}."
                                     f"{schema.copy_index.to_index}",
                            multi=schema.copy_index.multi,
                            script=schema.copy_index.script
                        ),
                        asynchronous=schema.asynchronous,
                        worker=schema.worker
                    ))

            else:
                schema.copy_index.from_index = f"{self.from_version.get_version_prefix()}." \
                                               f"{self.from_version.name}.{schema.copy_index.from_index}"
                schema.copy_index.to_index = f"{self.to_version.get_version_prefix()}." \
                                             f"{self.to_version.name}.{schema.copy_index.to_index}"
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

        for task_name, task_id in celery_task.wait():
            task = Task(
                timestamp=datetime.utcnow(),
                id=task_id,
                name=task_name,
                import_type="migration",
                event_type="<no-event-type>",
                import_id=task_id,
                task_id=task_id
            )

            await storage.driver.task.upsert_task(task)
