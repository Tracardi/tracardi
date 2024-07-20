from tracardi.config import tracardi
from tracardi.context import get_context, Context
from tracardi.domain import ExtraInfo
from tracardi.domain.migration_schema import MigrationSchema, CopyIndex
from typing import Optional, List, Dict
import json

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.elastic.driver.elastic_client import ElasticClient
from hashlib import sha1
from pathlib import Path
from tracardi.domain.version import Version
import re
from tracardi.worker.worker import run_migration_job
from typing import Union

logger = get_logger(__name__)

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
    "get_available_schemas()" which returns a dictionary of available schemas for the migration.
    The class also has an async method called "run()" which is used to run the migration job in an async
     way by using ThreadPoolExecutor and Celery worker.
    """

    available_migrations = {
        ("070", "071"): "070_to_071",
        ("071", "072"): "071_to_072",
        ("072", "073"): "072_to_073",
        ("073", "074"): "072_to_073",
        ("074", "080"): "074_to_080",
        ("080", "08x"): "080_to_08x",
        ("08x", "0820"): "08x_to_082x",  # from 0.8.1 to 0.8.2
        ("08x", "082x"): "08x_to_082x",
        ("082x", "0820"): "082x_to_0820",
        ("0820", "09x"): "0820_to_09x",
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

    def _get_migration_schemas_for_current_version(self) -> List[MigrationSchema]:
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
                f"{Path(__file__).parent}/elastic/{filename}.json",
                mode="r"
        ) as f:
            return [MigrationSchema(**schema) for schema in json.load(f) if isinstance(schema, dict)]  # avoid comments


    @staticmethod
    def _get_static_indices(version: str, tenant: str, index: str, production: bool) -> str:
        index = f"static-{version}.{tenant}.{index}"
        return index

    @staticmethod
    def _get_single_indices(version: str, tenant: str, index: str, production: bool) -> str:
        index = f"{version}.{tenant}.{index}"
        if production:
            index = f"prod-{index}"
        return index

    async def _get_partitioned_indices(self, template_name, production: bool):
        template = fr"{self.from_version}.{self.from_tenant}.{template_name}-[0-9]{{4}}-([0-9]{{1,2}}|q[1-4]|year)"

        if production:
            template = f"prod-{template}"

        es = ElasticClient.instance()
        return [index for index in await es.list_indices() if re.fullmatch(template, index)]

    async def get_available_schemas(self) -> Dict[str, Union[bool, List[MigrationSchema]]]:

        context = get_context()
        tenant = context.tenant

        if self.get_current_db_version_prefix(tracardi.version) != self.to_version or tenant != self.to_tenant:
            message = f"Installed system version is {tracardi.version.db_version} for tenant {tenant}, " \
                      f"but migration script is for version {self.to_version} for " \
                      f"tenant {self.to_tenant}."
            logger.error(message,
                         extra=ExtraInfo.build(object=self, origin="migration", error_number="M0002"))
            return {"warn": message, "schemas": []}

        schemas = self._get_migration_schemas_for_current_version()

        set_of_schemas_to_migrate = []

        for schema in schemas:
            if schema.copy_index.static is True:

                schema.copy_index.from_index = self._get_static_indices(
                    self.from_version,
                    self.from_tenant,
                    schema.copy_index.from_index,
                    production=context.production)

                schema.copy_index.to_index = self._get_static_indices(
                    self.to_version,
                    self.to_tenant,
                    schema.copy_index.to_index,
                    production=context.production)

                es = ElasticClient.instance()
                if await es.exists_index(schema.copy_index.from_index):
                    set_of_schemas_to_migrate.append(schema)
                else:
                    logger.warning(
                        f"Can't find the index {schema.copy_index.from_index}. Migration for this index will be stopped.",
                        extra=ExtraInfo.build(
                            object=self,
                            origin="migration",
                            error_number="M0001"
                        )
                    )

            elif schema.copy_index.multi is True:

                # Todo - now multi indices can have different suffixes, not only month

                from_partitioned_indices = await self._get_partitioned_indices(
                    template_name=schema.copy_index.from_index,
                    production=context.production)

                for from_index in from_partitioned_indices:

                    # Todo should migrate to the same partition

                    match_indices = re.findall(r'(-[0-9]{4}-[0-9]{1,2}|-[0-9]{4}-q[1-4]|-[0-9]{4}-year)', from_index)

                    if len(match_indices) == 0:
                        logger.error(
                            f"Could not find multi indices for {from_index}",
                            extra=ExtraInfo.build(
                                object=self,
                                origin="migration",
                                error_number="M0003"
                            )
                        )
                        continue

                    to_index = f"{schema.copy_index.to_index}{match_indices[0]}"

                    to_index = self._get_single_indices(self.to_version,
                                                        self.to_tenant,
                                                        to_index,
                                                        production=schema.copy_index.production)

                    if context.production:
                        to_index = f"prod-{to_index}"

                    set_of_schemas_to_migrate.append(MigrationSchema(
                        id=sha1(f"{from_index}{to_index}".encode("utf-8")).hexdigest(),
                        copy_index=CopyIndex(
                            from_index=from_index,
                            to_index=to_index,
                            production=schema.copy_index.production,
                            multi=schema.copy_index.multi,
                            script=schema.copy_index.script
                        ),
                        asynchronous=schema.asynchronous,
                        worker=schema.worker,
                        wait_for_completion=schema.wait_for_completion,
                        params=schema.params
                    ))

            else:
                schema.copy_index.from_index = self._get_single_indices(
                    self.from_version,
                    self.from_tenant,
                    schema.copy_index.from_index,
                    production=context.production)
                schema.copy_index.to_index = self._get_single_indices(
                    self.to_version,
                    self.to_tenant,
                    schema.copy_index.to_index,
                    production=context.production)

                es = ElasticClient.instance()
                if await es.exists_index(schema.copy_index.from_index):
                    set_of_schemas_to_migrate.append(schema)
                else:
                    logger.warning(
                        f"Can't find the index {schema.copy_index.from_index}. Migration for this index will be stopped.",
                        extra=ExtraInfo.build(
                            object=self,
                            origin="migration",
                            error_number="M0001"
                        )
                    )

        # TODO Warning disabled - save installation info in redis.
        warn = self.from_version in tracardi.version.upgrades

        # Change the destination if `copy-to-mysql`

        for schema in set_of_schemas_to_migrate:
            if schema.worker == 'copy_to_mysql':
                schema.copy_index.to_index = f"Table: {schema.params['mysql']}"

        return {"warn": warn, "schemas": set_of_schemas_to_migrate}

    async def start_migration(self, ids: List[str], elastic_host: str, context: Context) -> None:

        customized_schemas = await self.get_available_schemas()
        selected_schemas_for_migration = [schema.model_dump() for schema in customized_schemas["schemas"] if schema.id in ids]

        if not selected_schemas_for_migration:
            return

        run_migration_job(selected_schemas_for_migration, elastic_host, context.dict())

        await self.save_version_update()


    @classmethod
    def get_available_migrations_for_version(cls, version: Version) -> List[str]:
        return [migration[0] for migration in cls.available_migrations
                if migration[1] == MigrationManager.get_current_db_version_prefix(version)]

    async def save_version_update(self):
        # TODO Warning disabled - save installation info in redis. Now it is saved only in 1 instance memory
        tracardi.version.add_upgrade(self.from_version)


