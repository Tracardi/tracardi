import re
import aiomysql

from tracardi.context import get_context
from tracardi.domain.import_config import ImportConfig
from .importer import Importer
from pydantic import field_validator, BaseModel
from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.domain import resource as resource_db
from tracardi.process_engine.action.v1.connectors.mysql.query.model.connection import Connection
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from tracardi.worker.worker import run_mysql_import_job


class MySQLImportConfig(BaseModel):
    source: NamedEntity
    database_name: NamedEntity
    table_name: NamedEntity
    batch: int

    @field_validator("source", "database_name", "table_name")
    @classmethod
    def validate_named_entities(cls, value):
        if not value.id:
            raise ValueError(f"This field cannot be empty.")
        return value


class TableFetcherConfig(BaseModel):
    source: NamedEntity
    database_name: NamedEntity

    @field_validator("source", "database_name")
    @classmethod
    def validate_named_entities(cls, value):
        if not value.id:
            raise ValueError(f"This field cannot be empty.")
        return value


class DatabaseFetcherConfig(BaseModel):
    source: NamedEntity

    @field_validator("source")
    @classmethod
    def validate_named_entities(cls, value):
        if not value.id:
            raise ValueError(f"This field cannot be empty.")
        return value


class Endpoint(PluginEndpoint):

    @staticmethod
    async def fetch_databases(config: dict):
        config = DatabaseFetcherConfig(**config)
        resource = await resource_db.load(config.source.id)
        credentials = resource.credentials.production
        pool = await Connection(**credentials).connect()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(f"SHOW DATABASES")
                result = await cursor.fetchall()

                await cursor.close()
                conn.close()

                return {
                    "total": len(result),
                    "result": [{"name": list(record.values())[0], "id": list(record.values())[0]} for record in result]
                }

    @staticmethod
    async def fetch_tables(config: dict):
        config = TableFetcherConfig(**config)
        resource = await resource_db.load(config.source.id)
        credentials = resource.credentials.production
        pool = await Connection(**credentials).connect()

        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                stripped_database_name = re.sub(r'\W+', '', config.database_name.id)
                await cursor.execute(f"SHOW TABLES FROM {stripped_database_name}")

                result = await cursor.fetchall()
                await cursor.close()
                conn.close()

                return {
                    "total": len(result),
                    "result": [{"name": list(record.values())[0], "id": list(record.values())[0]} for record in result]
                }


class MySQLTableImporter(Importer):
    config_model = MySQLImportConfig

    init = {
        "source": {"name": "", "id": ""},
        "database_name": {"name": "", "id": ""},
        "table_name": {"name": "", "id": ""},
        "batch": 100,
    }

    form = Form(groups=[FormGroup(
        fields=[
            FormField(
                name="MySQL resource",
                id="source",
                description="Select MySQL resource you want to connect to. Resource must have database credentials defined.",
                component=FormComponent(type="resource", props={"tag": "mysql"})
            ),
            FormField(
                name="Database name",
                id="database_name",
                description="Select database that you want to fetch data from.",
                component=FormComponent(type="autocomplete", props={
                    "label": "Database",
                    "endpoint": {
                        "url": Endpoint.url(__name__, "fetch_databases"),
                        "method": "post"
                    }
                })
            ),
            FormField(
                name="Table name",
                id="table_name",
                description="Select table that you want to fetch data from.",
                component=FormComponent(type="autocomplete", props={
                    "label": "Table",
                    "endpoint": {
                        "url": Endpoint.url(__name__, "fetch_tables"),
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

    async def run(self, task_name, import_config: ImportConfig):

        config = MySQLImportConfig(**import_config.config)
        resource = await resource_db.load(config.source.id)
        credentials = resource.credentials.test if self.debug is True else resource.credentials.production

        run_mysql_import_job(
            task_name,
            import_config.model_dump(mode='json'),
            credentials,
            get_context()
        )
