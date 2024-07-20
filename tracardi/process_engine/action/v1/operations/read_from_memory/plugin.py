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
from tracardi.service.secrets import b64_decoder


def validate(config: dict) -> Config:
    return Config(**config)


class ReadFromMemoryAction(ActionRunner):

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
        try:
            dot = self._get_dot_accessor(payload)
            key = dot[self.config.key]
            prefix = self.config.prefix.strip()
            if prefix:
                key = f"{Collection.plugin_memory}{prefix}:{key}"
            else:
                key = f"{Collection.plugin_memory}{key}"
            result = self.client.get(name=key)
            if result is None:
                return Result(port="not-exists", value=payload)
            return Result(port="success", value={"value": b64_decoder(result)})

        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ReadFromMemoryAction',
            inputs=["payload"],
            outputs=["success", "not-exists", "error"],
            version='0.8.0',
            license="MIT + CC",
            author="Dawid Kruk, Risto Kowaczewski",
            init={
                "resource": {
                    "name": "",
                    "id": ""
                },
                "key": "",
                "prefix": ""
            },
            manual="read_from_memory_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Read from memory",
                        fields=[
                            FormField(
                                id="resource",
                                name="Resource",
                                description="Select remote redis server or leave it empty to read from local server.",
                                component=FormComponent(type="resource", props={"label": "Redis server", "tag": "redis"})
                            ),
                            FormField(
                                id="key",
                                name="Key",
                                description="Provide a key where the data will be stored. Think of a “key” as a "
                                            "unique identifier and a “value” as whatever data you want to associate "
                                            "with that key. Key can ba a value from profile, event, etc.",
                                component=FormComponent(type="dotPath", props={"label": "Key"})
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
            name='Read from Redis',
            desc='Reads value with given key from cross-instance memory.',
            icon='redis',
            group=["Redis"],
            tags=['redis'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port returns data from memory if data was successfully read."),
                    "not-exists": PortDoc(desc="This port returns payload if data does not exist."),
                    "error": PortDoc(desc="This port returns some error detail if there was an error while reading data"
                                          " from memory.")
                }
            )
        )
    )
