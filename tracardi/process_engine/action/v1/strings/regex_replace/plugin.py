from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.action_runner import ActionRunner
import re
from .model.config import Config


def validate(config: dict) -> Config:
    return Config(**config)


class RegexReplacer(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        self.config.string = dot[self.config.string]
        self.config.replace_with = dot[self.config.replace_with]

        if re.search(self.config.find_regex, self.config.string):
            return Result(port="replaced", value={"value": re.sub(
                self.config.find_regex,
                self.config.replace_with,
                self.config.string
            )})
        else:
            return Result(port="not_found", value={"value": self.config.string})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='RegexReplacer',
            inputs=["payload"],
            outputs=["replaced", "not_found"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            init={
                "string": None,
                "replace_with": None,
                "find_regex": None
            },
            manual="regex_replace_action",
            form=Form(
                name="Plugin configuration",
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="string",
                                name="String",
                                description="Please provide path to the text that you want to change by replacing "
                                            "fragments of it.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="replace_with",
                                name="Replace with",
                                description="Please provide a path to the text that you want to replace matched "
                                            "fragments with.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="find_regex",
                                name="Regex",
                                description="Please provide a regular expression matching fragments of text that you "
                                            "want to replace.",
                                component=FormComponent(type="text", props={"label": "Regex"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Regex string replace',
            desc='Replaces pieces of string that match provided regex with given value.',
            type='flowNode',
            icon='regex',
            group=["Regex"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "replaced": PortDoc(desc="This port returns string after replacing."),
                    "not_found": PortDoc(desc="This port returns string if no matches were found.")
                }
            )
        )
    )
