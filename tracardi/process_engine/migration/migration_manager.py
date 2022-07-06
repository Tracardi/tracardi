from tracardi.domain.migration_schema import MigrationSchema, CopyIndex
from typing import Optional, List, Dict
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
import re


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
        template = fr"{self.from_version.get_version_prefix()}." \
                   fr"{self.from_version.name}.{template_name}-[0-9]{'{4}'}-[0-9]+"
        es = ElasticClient.instance()
        return [index for index in await es.list_indices() if re.fullmatch(template, index)]

    async def get_customized_schemas(self) -> List[MigrationSchema]:
        general_schemas = self.get_schemas()

        customized_schemas = []
        for schema in general_schemas:
            if schema.copy_index.multi is True:
                from_indices = await self.get_multi_indices(template_name=schema.copy_index.from_index)
                for from_index in from_indices:
                    to_index = f"{schema.copy_index.to_index}{re.findall(r'-[0-9]{4}-[0-9]+', from_index)[0]}"
                    customized_schemas.append(MigrationSchema(
                        id=sha1(f"{from_index}{to_index}".encode("utf-8")).hexdigest(),
                        copy_index=CopyIndex(
                            from_index=from_index,
                            to_index=f"{self.to_version.get_version_prefix()}.{self.to_version.name}.{to_index}",
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
                customized_schemas.append(schema)

        return customized_schemas

    async def start_migration(self, ids: List[str], elastic_host: str) -> Dict[str, Optional[List[List[str]]]]:

        final_schemas = [schema.dict() for schema in await self.get_customized_schemas() if schema.id in ids]

        if not final_schemas:
            return {"started_migrations": None}

        def add_to_celery(given_schemas: List, elastic: str):
            return run_migration_job.delay(given_schemas, elastic)

        executor = ThreadPoolExecutor(
            max_workers=1,
        )
        loop = asyncio.get_running_loop()
        blocking_tasks = [loop.run_in_executor(executor, add_to_celery, final_schemas, elastic_host)]
        completed, pending = await asyncio.wait(blocking_tasks)
        celery_task = completed.pop().result()

        started_migration_tasks = []
        for task_name, task_id in celery_task.wait(timeout=40.0, propagate=True):
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

            started_migration_tasks.append([task_name, task_id])

        return {"started_migrations": started_migration_tasks}

