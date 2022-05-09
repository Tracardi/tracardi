import json
from datetime import datetime, date
import aiomysql
from .batch_runner import BatchRunner
from pydantic import BaseModel
from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.driver import storage
from tracardi.process_engine.action.v1.connectors.mysql.query.model.connection import Connection
from tracardi.service.storage.redis_client import RedisClient
import asyncio
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint


class MySQLBatchConfig(BaseModel):
    source: NamedEntity
    table_name: str
    batch: int
    event_type: str


class TableFetchConfig(BaseModel):
    source: NamedEntity


class Endpoint(PluginEndpoint):

    @staticmethod
    async def fetch_tables(config: dict):
        config = TableFetchConfig(**config)
        resource = await storage.driver.resource.load(config.source.id)
        credentials = resource.credentials.production
        pool = await Connection(**credentials).connect()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(f"SHOW TABLES;")
                result = await cursor.fetchall()

                return {
                    "total": len(result),
                    "result": [{"name": list(record.values())[0], "id": list(record.values())[0]} for record in result]
                }


class MySQLBatch(BatchRunner):
    config_class = MySQLBatchConfig
    init = {"source": {"name": "", "id": ""}, "table_name": None, "batch": 100, "event_type": None}
    form = Form(groups=[FormGroup(name="MySQL config", fields=[
        FormField(
            name="MySQL resource",
            id="source",
            description="Select your MySQL resource",
            component=FormComponent(type="resource", props={"tag": "mysql"})
        ),
        FormField(
            name="Table name",
            id="table_name",
            description="Provide a name of the table that you want to fetch data from.",
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
            description="Provide a number of records that you want to fetch from given MySQL table.",
            component=FormComponent(type="text", props={"label": "Batch"})
        ),
        FormField(
            name="Event type",
            id="event_type",
            description="Provide type of the event that you want to be triggered for every record when fetched. This "
                        "event will contain all columns with their values, attached in its properties.",
            component=FormComponent(type="text", props={"label": "Event type"})
        )
    ])])

    @staticmethod
    def to_dict(record):
        def json_default(obj):
            """JSON serializer for objects not serializable by default json code"""

            if isinstance(obj, (datetime, date)):
                return obj.isoformat()

            return obj.decode('utf-8')

        j = json.dumps(dict(record), default=json_default)
        return json.loads(j)

    async def run(self, config: dict, task_id: str):
        self.config = MySQLBatchConfig(**config)
        resource = await storage.driver.resource.load(self.config.source.id)
        credentials = resource.credentials.test if self.debug is True else resource.credentials.production
        pool = await Connection(**credentials).connect()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(f"SELECT COUNT(1) as count FROM {self.config.table_name};")
                quantity = (await cursor.fetchone())["count"]

                redis_client = RedisClient()

                # UPDATE PROGRESS
                for x in range(0, 101):
                    await asyncio.sleep(0.5)
                    redis_client.client.set(f"TASK-{task_id}", x/100.0, ex=60 * 60)
                pool.close()
                await pool.wait_closed()
