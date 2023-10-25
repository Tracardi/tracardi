from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.wf.domain.edge import Edge
from .model.config import Config
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class PayloadMemoryCollector(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge: Edge = None) -> Result:

        if self.config.name in self.memory:

            if self.config.type == 'list' and not isinstance(self.memory[self.config.name], list):
                raise ValueError(f"Memory has key {self.config.name} and it is not a list.")

            elif self.config.type == 'dict' and not isinstance(self.memory[self.config.name], dict):
                raise ValueError(f"Memory has key {self.config.name} and it is not a dictionary.")

        if self.config.name not in self.memory:
            if self.config.type == 'dict':
                self.memory[self.config.name] = {}
            elif self.config.type == 'list':
                self.memory[self.config.name] = []

        if self.config.type == 'dict':
            if not in_edge.has_name():
                raise ValueError(f"Edge id {in_edge.id} has no name. Could not create object with payload value. "
                                 f"Edge name is used to save payload value.")

            self.memory[self.config.name][in_edge.data.name.replace(" ", "-")] = payload
        elif self.config.type == 'list':
            self.memory[self.config.name].append(payload)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='PayloadMemoryCollector',
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "name": None,
                "type": "list"
            },
            manual="memory/payload_memory_collector",
            form=Form(
                groups=[
                    FormGroup(
                        name="Payload memory collector configuration",
                        fields=[
                            FormField(
                                id="name",
                                name="Name of collection",
                                description="Please provide the name under which the collection will be saved.",
                                component=FormComponent(type="text", props={"label": "Name"})
                            ),
                            FormField(
                                id="type",
                                name="Type of collection",
                                description="Select type of collection. Type of `Dictionary` requires named connections "
                                            "in the workflow.",
                                component=FormComponent(type="select", props={"label": "Name", "items": {
                                    "list": "List",
                                    "dict": "Dictionary"
                                }})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Payload collector',
            desc='Collects input payloads in the workflow memory object.',
            tags=['memory', 'join'],
            icon='array',
            group=["Operations"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload.")
                }
            )
        )
    )
