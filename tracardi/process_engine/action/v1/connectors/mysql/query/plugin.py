import json
from typing import Any

import aiomysql
from datetime import datetime, date
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.domain import resource as resource_db
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration
from .model.connection import Connection


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class MysqlConnectorAction(ActionRunner):

    connection: Connection
    config: Configuration
    pool: Any = None

    async def set_up(self, init):

        configuration = validate(init)
        resource = await resource_db.load(configuration.source.id)

        self.config = configuration
        self.connection = resource.credentials.get_credentials(self, output=Connection)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            # Prepare statement data
            template = DictTraverser(self._get_dot_accessor(payload))
            data = template.reshape(self.config.data)
            self.console.log("Executing query: {} with data: {}".format(self.config.query, data))

            self.pool = await self.connection.connect(self.config.timeout)

            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    if self.config.type == 'call':
                        # todo implement

                        return Result(port="result", value={"result": payload})
                    else:
                        if len(data) > 0:
                            await cursor.execute(self.config.query, tuple(data))
                        else:
                            await cursor.execute(self.config.query)

                        if self.config.type in ['insert', 'delete', 'update']:
                            await conn.commit()
                            if self.config.type == 'insert':
                                return Result(port="result", value={"last_insert_id": cursor.lastrowid})
                        if self.config.type == 'select':
                            result = await cursor.fetchall()
                            result = [self.to_dict(record) for record in result]
                            return Result(port="result", value={"result": result})

                    return Result(port="result", value=payload)

        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={"payload": payload, "error": str(e)})

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    async def on_error(self, *args, **kwargs):
        await self.close()

    @staticmethod
    def to_dict(record):

        def json_default(obj):
            """JSON serializer for objects not serializable by default json code"""

            if isinstance(obj, (datetime, date)):
                return obj.isoformat()

            return obj.decode('utf-8')

        j = json.dumps(dict(record), default=json_default)
        return json.loads(j)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MysqlConnectorAction',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.6.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="mysql_connector_action",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "type": "select",
                "query": "SELECT 1",
                "data": [],
                "timeout": 10
            },
            form=Form(groups=[
                FormGroup(
                    name="MySQL Resource",
                    fields=[
                        FormField(
                            id="source",
                            name="MySQL resource",
                            description="Select MySQL resource. Credentials from selected resource will be used "
                                        "to connect to database.",
                            component=FormComponent(type="resource", props={"label": "resource", "tag": "mysql"})
                        )
                    ]
                ),
                FormGroup(
                    name="MySQL Query",
                    fields=[
                        FormField(
                            id="type",
                            name="SQL type",
                            description="Select SQL query type. It must match typed SQL statement otherwise it may not "
                                        "execute properly.",
                            component=FormComponent(
                                type="select",
                                props={
                                    "label": "SQL type",
                                    "items": {
                                        "select": "SELECT",
                                        "insert": "INSERT",
                                        "delete": "DELETE",
                                        "create": "CREATE",
                                        "update": "UPDATE",
                                    }
                                })
                        ),
                        FormField(
                            id="query",
                            name="SQL statement",
                            description="Type prepared SQL query to be executed in MySQL. Use `%s` for data "
                                        "placeholders. Below tape data to replace placeholder.",
                            component=FormComponent(
                                type="sql",
                                props={
                                    "label": "SQL"
                                })
                        ),
                        FormField(
                            id="data",
                            name="Data for SQL statement",
                            description="Type data for prepared SQL statement. Data must be a list "
                                        "of values or paths to values. It will replace %s placeholders in SQL "
                                        "statement. It will replace placeholders one by one so order matters.",
                            component=FormComponent(
                                type="listOfDotPaths",
                                props={"label": "List of data", "allowDuplicates": True})
                        )
                    ]
                ),
                FormGroup(
                    name="Advanced MySQL Configuration",
                    fields=[
                        FormField(
                            id="timeout",
                            name="Connection time-out",
                            description="Type SQL query connection time-out",
                            component=FormComponent(
                                type="text",
                                props={
                                    "label": "Time-out"
                                })
                        )
                    ]
                ),
            ]),

        ),
        metadata=MetaData(
            name='MySQL connector',
            desc='Connects to mysql and reads data.',
            icon='mysql',
            group=["Databases"],
            tags=['database', 'sql'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns query result."),
                    "error": PortDoc(desc="Gets triggered if an error occurs.")
                }
            )
        )
    )
