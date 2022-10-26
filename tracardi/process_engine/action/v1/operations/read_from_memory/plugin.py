from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormField, \
    FormGroup, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.plugin.domain.result import Result
from tracardi.service.secrets import b64_decoder


def validate(config: dict) -> Config:
    return Config(**config)


class ReadFromMemoryAction(ActionRunner):

    client: RedisClient
    config: Config

    async def set_up(self, init):
        self.config = validate(init)
        self.client = RedisClient()

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            result = self.client.client.get(name=f"TRACARDI-USER-MEMORY-{self.config.key}")
            return Result(port="success", value={"value": b64_decoder(result)})

        except Exception as e:
            return Result(port="error", value={"detail": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ReadFromMemoryAction',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.3',
            license="MIT",
            author="Dawid Kruk",
            init={
                "key": None
            },
            manual="read_from_memory_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Read from memory",
                        fields=[
                            FormField(
                                id="key",
                                name="Key",
                                description="Provide a key associated with data that you want to get from memory.",
                                component=FormComponent(type="text", props={"label": "Key"})
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
                    "success": PortDoc(desc="This port returns payload if data was successfully read from memory."),
                    "error": PortDoc(desc="This port returns some error detail if there was an error while reading data"
                                          " from memory.")
                }
            )
        )
    )
