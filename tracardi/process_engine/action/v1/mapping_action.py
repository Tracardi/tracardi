from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from pydantic import validator
from typing import Dict, Any
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    value: str
    case_sensitive: bool
    mapping: Dict[str, Any]

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator('mapping')
    def validate_mapping(cls, value, values):
        if not value:
            raise ValueError("Mapping cannot be empty.")
        if not values["case_sensitive"] and len({key.lower() for key in value}) != len(value):
            raise ValueError("Inserting two keys that differ only in letter case without case sensitivity enabled, "
                             "may cause plugin malfunction.")
        return value


def validate(config: dict):
    return Config(**config)


class MappingAction(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        value = dot[self.config.value].lower() \
            if not self.config.case_sensitive and isinstance(dot[self.config.value], str) else dot[self.config.value]

        mapping = {
            dot[key].lower() if not self.config.case_sensitive and isinstance(dot[key], str) else dot[key]:
                dot[value].lower() if not self.config.case_sensitive and isinstance(dot[value], str) else dot[value]
            for key, value in self.config.mapping.items()
        }

        value = mapping.get(value, None)

        return Result(port="result", value={"value": value})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MappingAction',
            inputs=["payload"],
            outputs=["result"],
            version='0.6.1',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="mapping_action",
            init={
                "value": None,
                "case_sensitive": False,
                "mapping": {}
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Mapping configuration",
                        fields=[
                            FormField(
                                id="value",
                                name="Value",
                                description="Please type a reference path to the value to match.",
                                component=FormComponent(type="dotPath",
                                                        props={"label": "Value", "defaultSourceValue": "payload"})
                            ),
                            FormField(
                                id="case_sensitive",
                                name="Case sensitivity",
                                description="Should the value be lowercased before mapping?",
                                component=FormComponent(type="bool", props={"label": "Enable case sensitivity"})
                            ),
                            FormField(
                                id="mapping",
                                name="Set of replacements",
                                description="Please provide key-value pairs. The value will be returned if the referenced "
                                            "value is the same as the key from this set.",
                                component=FormComponent(type="keyValueList", props={"label": "List"})
                            )
                        ]
                    )
                ]
            )

        ),
        metadata=MetaData(
            name='Value mapping',
            desc='It returns matching value from the set of data.',
            icon='map-properties',
            keywords=['switch', 'matching'],
            group=["Data processing"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This ports returns matched value.")
                }
            )
        )
    )
