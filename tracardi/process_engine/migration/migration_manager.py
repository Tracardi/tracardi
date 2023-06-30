from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.migration_schema import MigrationSchema, CopyIndex
from typing import Optional, List, Dict
import json
from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.worker.celery_worker import run_migration_job
import asyncio
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha1
from pathlib import Path
from tracardi.domain.version import Version
import re
from tracardi.service.storage.index import Resource
from typing import Union


class MigrationNotFoundException(Exception):
    pass


class MigrationManager:

    """
    This code defines a class which is used to handle the migration of data between
    different versions of the software. The class has two attributes, "from_version" and "to_version",
    which are used to specify the source and destination versions of the migration. The class also has a
    dictionary "available_migrations" which maps tuples of source and destination versions to the name of the
    migration script that should be used. The class has several methods, including "get_schemas()", which loads
    the migration script corresponding to the source and destination versions specified in the attributes,
    "get_multi_indices()" which returns a list of indices that match a given template name, and
    "get_customized_schemas()" which returns a dictionary of customized schemas for the migration.
    The class also has an async method called "run()" which is used to run the migration job in an async
     way by using ThreadPoolExecutor and Celery worker.
    """

    available_migrations = {
        ("070", "071"): "070_to_071",
        ("071", "072"): "071_to_072",
        ("072", "073"): "072_to_073",
        ("073", "074"): "072_to_073",
        ("074", "080"): "074_to_080",
        ("080", "08x"): "080_to_08x"
    }

    def __init__(self, from_version: str, to_version: str, from_prefix: Optional[str] = None,
                 to_prefix: Optional[str] = None):
        self.from_version = from_version
        self.from_tenant = from_prefix
        self.to_version = to_version
        self.to_tenant = to_prefix

    @staticmethod
    def get_current_db_version_prefix(version: Version):
        return version.db_version.replace(".", "")

    def get_schemas(self):
        try:
            filename = self.available_migrations[
                (self.from_version, self.to_version)
            ]

        except KeyError:
            raise MigrationNotFoundException(
                f"Migration from {self.from_version} to {self.to_version} "
                f"not found."
            )

        with open(
                f"{Path(__file__).parent}/schemas/{filename}.json",
                mode="r"
        ) as f:
            return [MigrationSchema(**schema) for schema in json.load(f) if isinstance(schema, dict)]  # avoid comments

    async def get_multi_indices(self, template_name):
        template = fr"{self.from_version}." \
                   fr"{self.from_tenant}.{template_name}-[0-9]{'{4}'}-[0-9]+"
        es = ElasticClient.instance()
        return [index for index in await es.list_indices() if re.fullmatch(template, index)]

    async def get_customized_schemas(self) -> Dict[str, Union[bool, List[MigrationSchema]]]:

        tenant = get_context().tenant

        if self.get_current_db_version_prefix(tracardi.version) != self.to_version or tenant != self.to_tenant:
            raise ValueError(f"Installed system version is {tracardi.version.db_version} for tenant {tenant}, "
                             f"but migration script is for version {self.to_version} for "
                             f"tenant {self.to_tenant}.")

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
                            to_index=f"{self.to_version}.{self.to_tenant}.{to_index}",
                            multi=schema.copy_index.multi,
                            script=schema.copy_index.script
                        ),
                        asynchronous=schema.asynchronous,
                        worker=schema.worker,
                        wait_for_completion=schema.wait_for_completion
                    ))

            else:
                schema.copy_index.from_index = f"{self.from_version}." \
                                               f"{self.from_tenant}.{schema.copy_index.from_index}"
                schema.copy_index.to_index = f"{self.to_version}." \
                                             f"{self.to_tenant}.{schema.copy_index.to_index}"

                es = ElasticClient.instance()
                if await es.exists_index(schema.copy_index.from_index):
                    customized_schemas.append(schema)
                else:
                    print(f"Can't find the index {schema.copy_index.from_index}")

        # TODO Warning disabled - save installation info in redis.
        warn = self.from_version in tracardi.version.upgrades

        return {"warn": warn, "schemas": customized_schemas}

    async def start_migration(self, ids: List[str], elastic_host: str) -> None:

        customized_schemas = await self.get_customized_schemas()
        final_schemas = [schema.dict() for schema in customized_schemas["schemas"] if schema.id in ids]

        if not final_schemas:
            return

        def add_to_celery(given_schemas: List, elastic: str, task_index_name: str):
            return run_migration_job.delay(given_schemas, elastic, task_index_name)

        task_index = Resource().get_index_constant("task").get_write_index()

        # Run in executor

        executor = ThreadPoolExecutor(
            max_workers=1,
        )
        loop = asyncio.get_running_loop()
        blocking_tasks = [loop.run_in_executor(executor, add_to_celery, final_schemas, elastic_host, task_index)]
        completed, pending = await asyncio.wait(blocking_tasks)
        celery_task = completed.pop().result()

        await self.save_version_update()

        return celery_task.id

    @classmethod
    def get_available_migrations_for_version(cls, version: Version) -> List[str]:
        return [migration[0] for migration in cls.available_migrations
                if migration[1] == MigrationManager.get_current_db_version_prefix(version)]

    async def save_version_update(self):
        # TODO Warning disabled - save installation info in redis. Now it is saved only in 1 instance memory
        tracardi.version.add_upgrade(self.from_version)


