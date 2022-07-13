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
from celery.exceptions import TimeoutError as CeleryTimeoutError
from tracardi.service.storage.index import resources


class MigrationNotFoundException(Exception):
    pass


class MigrationManager:
    available_migrations = {
        ("0.7.0", "0.7.1"): "test"
    }

    def __init__(self, from_version: str, to_version: str, from_prefix: Optional[str] = None,
                 to_prefix: Optional[str] = None):
        self.from_version = Version(version=from_version, name=from_prefix)
        self.to_version = Version(version=to_version, name=to_prefix)

    def get_schemas(self):
        try:
            filename = self.available_migrations[
                (self.from_version.version, self.to_version.version)
            ]

        except KeyError:
            raise MigrationNotFoundException(
                f"Migration from {self.from_version.version} to {self.to_version.version} "
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
        es = ElasticClient.instance()
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
                if await es.exists_index(schema.copy_index.from_index):
                    customized_schemas.append(schema)

        return customized_schemas

    async def start_migration(self, ids: List[str], elastic_host: str) -> None:

        final_schemas = [schema.dict() for schema in await self.get_customized_schemas() if schema.id in ids]

        if not final_schemas:
            return

        def add_to_celery(given_schemas: List, elastic: str, task_index_name: str):
            return run_migration_job.delay(given_schemas, elastic, task_index_name)

        task_index = resources.get_index("task").get_write_index()

        executor = ThreadPoolExecutor(
            max_workers=1,
        )
        loop = asyncio.get_running_loop()
        blocking_tasks = [loop.run_in_executor(executor, add_to_celery, final_schemas, elastic_host, task_index)]
        completed, pending = await asyncio.wait(blocking_tasks)
        celery_task = completed.pop().result()

        return celery_task.id

    @classmethod
    def get_available_migrations_for_version(cls, version: Version) -> List[str]:
        return [migration[0] for migration in cls.available_migrations if migration[1] == version.version]

