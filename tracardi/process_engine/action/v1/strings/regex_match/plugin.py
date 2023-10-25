from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from .model.model import Configuration
import re


def search(pattern, text):
    result = re.findall(pattern, text)
    if result is None:
        return None
    return result


def validate(config: dict):
    return Configuration(**config)


class RegexMatchAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        text = dot[self.config.text]
        result = search(self.config.pattern, text)

        dictionary = {}
        if result is not None:
            for i, match in enumerate(result):
                dictionary[f"{self.config.group_prefix}-{i}"] = match
        else:
            self.console.warning("Regex couldn't find anything matching the pattern from supplied string.")
        return Result(port="payload", value=dictionary)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.strings.regex_match.plugin',
            className='RegexMatchAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.0.1',
            license="MIT + CC",
            author="Patryk Migaj",
            manual="regex/regex_match",
            init={
                "pattern": "<pattern>",
                "text": "<text or path to text>",
                "group_prefix": "Group"
            },
            form=Form(
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="pattern",
                                name="Regex pattern",
                                description="Provide regular expression string to match with provided text.",
                                component=FormComponent(type="text", props={"label": "Pattern"})
                            ),
                            FormField(
                                id="text",
                                name="Path to text",
                                description="Provide path to field with text to match.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="group_prefix",
                                name="Group prefix",
                                description="Provide group prefix for regex matching.",
                                component=FormComponent(type="text", props={"label": "Group prefix"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Regex match',
            desc='This plugin use regex matching and returns matched data.',
            icon='regex',
            group=["Regex"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns matched groups."),
                }
            ),
        )
    )
