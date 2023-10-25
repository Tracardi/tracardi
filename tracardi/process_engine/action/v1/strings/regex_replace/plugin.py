from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
import re
from .model.config import Config


def validate(config: dict) -> Config:
    return Config(**config)


class RegexReplacer(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        string = dot[self.config.string]
        replace_with = dot[self.config.replace_with]

        if re.search(self.config.find_regex, string):
            return Result(port="replaced", value={"value": re.sub(
                self.config.find_regex,
                replace_with,
                string
            )})
        else:
            return Result(port="not_found", value={"value": string})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='RegexReplacer',
            inputs=["payload"],
            outputs=["replaced", "not_found"],
            version='0.6.1',
            license="MIT + CC",
            author="Dawid Kruk",
            init={
                "string": None,
                "replace_with": None,
                "find_regex": None
            },
            manual="regex_replace_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Regex replace configuration",
                        fields=[
                            FormField(
                                id="string",
                                name="String",
                                description="Please provide a path to the text (or the text itself) that you want to "
                                            "change.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="replace_with",
                                name="Replace with",
                                description="Please provide the text that replaces the matched substring.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="find_regex",
                                name="Regex",
                                description="Please provide a regular expression to match text (substring) to be "
                                            "replaced.",
                                component=FormComponent(type="text", props={"label": "Regex"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Regex replace',
            desc='Replaces a substring that matches regex pattern with the given replacement string.',
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
