from typing import Any, Union

import redis

from tracardi.config import RedisConfig
from tracardi.domain.resources.redis_resource import RedisCredentials
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormField, \
    FormGroup, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.domain import resource as resource_db
from tracardi.service.storage.redis.collections import Collection
from .model.config import Config
from tracardi.service.storage.redis.driver.redis_client import RedisClient
from tracardi.service.plugin.domain.result import Result
from tracardi.service.secrets import b64_encoder


def validate(config: dict) -> Config:
    return Config(**config)


class WriteToMemoryAction(ActionRunner):

    client: Union[RedisClient, Any]
    config: Config

    async def set_up(self, init):
        self.config = validate(init)

        if self.config.resource.id == "":
            self.client = RedisClient()
        else:
            resource = await resource_db.load(self.config.resource.id)
            credentials = resource.credentials.get_credentials(self, output=RedisCredentials)

            uri = RedisConfig.get_redis_uri(
                credentials.url,
                credentials.user,
                credentials.password,
                credentials.protocol,
                credentials.database
            )
            self.client = redis.from_url(uri)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)

        value = dot[self.config.value]
        value = b64_encoder(value)

        key = dot[self.config.key]

        prefix = self.config.prefix.strip()
        if prefix:
            key = f"{Collection.plugin_memory}{prefix}:{key}"
        else:
            key = f"{Collection.plugin_memory}{key}"

        try:
            self.client.set(
                name=key,
                value=value,
                ex=self.config.ttl if self.config.ttl > 0 else None
            )
            return Result(port="success", value=payload)

        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='WriteToMemoryAction',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.8.0',
            license="MIT + CC",
            author="Dawid Kruk, Risto Kowaczewski",
            init={
                "key": "",
                "prefix": "",
                "value": "",
                "ttl": 15,
                "resource": {
                    "name": "",
                    "id": ""
                }
            },
            manual="write_to_memory_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Write to memory",
                        fields=[
                            FormField(
                                id="resource",
                                name="Resource",
                                description="Select remote redis server or leave it empty to read from local server.",
                                component=FormComponent(type="resource",
                                                        props={"label": "Redis server", "tag": "redis"})
                            ),
                            FormField(
                                id="key",
                                name="Key",
                                description="Provide a key for this data. Data will be accessible by providing this "
                                            "key in Read from memory plugin.",
                                component=FormComponent(type="dotPath", props={"label": "Key"})
                            ),
                            FormField(
                                id="value",
                                name="Path to value",
                                description="Provide the path to value that you want to be associated with given key.",
                                component=FormComponent(type="dotPath", props={"label": "Value"})
                            ),
                            FormField(
                                id="ttl",
                                name="Time to live",
                                description="Provide a number of seconds for the value to live. After this amount "
                                            "of time, the value will be deleted.",
                                component=FormComponent(type="text", props={"label": "Time to live"})
                            ),
                            FormField(
                                id="prefix",
                                name="Key prefix",
                                description="Type key prefix if you would like to store different values for the "
                                            "same key. Key prefix can be any string. Leave empty if you do no need "
                                            "to prefix the key.",
                                component=FormComponent(type="text", props={"label": "Prefix"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Write to Redis',
            desc='Writes given data to cross-instance memory.',
            icon='redis',
            group=["Redis"],
            tags=['redis'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port returns payload if data was successfully written to memory."),
                    "error": PortDoc(desc="This port returns some error detail if there was an error while writing data"
                                          " to memory.")
                }
            )
        )
    )
