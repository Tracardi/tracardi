from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from pydantic import BaseModel, validator
from typing import List
from random import randint
from tracardi.service.plugin.domain.result import Result


class Config(BaseModel):
    list_of_items: List[str]

    @validator("list_of_items")
    def validate_list_of_items(cls, value):
        if not value:
            raise ValueError("This list have to contain at least one element.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class RandomItemAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)

        random_value_dot = self.config.list_of_items.pop(randint(0, len(self.config.list_of_items) - 1))
        random_value = dot[random_value_dot]

        return Result(port="random_element", value={"value": random_value})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='RandomItemAction',
            inputs=["payload"],
            outputs=["random_element"],
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            manual="random_element_action",
            init={
                "list_of_items": []
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Random item configuration",
                        fields=[
                            FormField(
                                id="list_of_items",
                                name="List of items",
                                description="Provide a list of paths to values that plugin will choose randomly from.",
                                component=FormComponent(type="listOfDotPaths", props={
                                    "label": "List",
                                    "defaultMode": 2
                                })
                            )
                        ]
                    )
                ]
            )

        ),
        metadata=MetaData(
            name='Random item',
            desc='Returns a random value from list given in configuration.',
            icon='shuffle',
            group=["Data processing"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "random_element": PortDoc(desc="This port returns a random item from defined list.")
                }
            )
        )
    )
