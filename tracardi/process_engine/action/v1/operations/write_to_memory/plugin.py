from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormField, \
    FormGroup, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.plugin.domain.result import Result
from tracardi.service.secrets import b64_encoder


def validate(config: dict) -> Config:
    return Config(**config)


class WriteToMemoryAction(ActionRunner):

    client: RedisClient
    config: Config

    async def set_up(self, init):
        self.config = validate(init)
        self.client = RedisClient()

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        value = dot[self.config.value]
        value = b64_encoder(value)

        try:
            self.client.client.set(
                name=f"TRACARDI-USER-MEMORY-{self.config.key}",
                value=value,
                ex=self.config.ttl
            )
            return Result(port="success", value=payload)

        except Exception as e:
            return Result(port="error", value={"detail": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='WriteToMemoryAction',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.3',
            license="MIT",
            author="Dawid Kruk",
            init={
                "key": None,
                "value": None,
                "ttl": 15
            },
            manual="write_to_memory_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Write to memory",
                        fields=[
                            FormField(
                                id="key",
                                name="Key",
                                description="Provide a key for this data. Data will be accessible by providing this "
                                            "key in Read from memory plugin.",
                                component=FormComponent(type="text", props={"label": "Key"})
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
