from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from pydantic import field_validator
from typing import List
from random import randint
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    list_of_items: List[str]

    @field_validator("list_of_items")
    @classmethod
    def validate_list_of_items(cls, value):
        if not value:
            raise ValueError("This list has to contain at least one element.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class RandomItemAction(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
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
            license="MIT + CC",
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
            purpose=['segmentation', 'collection'],
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
