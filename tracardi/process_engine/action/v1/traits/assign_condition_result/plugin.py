from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.process_engine.tql.condition import Condition
from tracardi.domain.profile import Profile
from .model.config import Config


def validate(config: dict) -> Config:
    return Config(**config)


class AssignConditionResultPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        condition = Condition()
        dot = self._get_dot_accessor(payload)

        for key, value in self.config.conditions.items():
            dot[key] = await condition.evaluate(value, dot)

        profile = Profile(**dot.profile)
        self.profile.replace(profile)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AssignConditionResultPlugin',
            inputs=["payload"],
            outputs=["payload"],
            version='0.8.2',
            license="MIT + CC",
            author="Dawid Kruk, Risto Kowaczewski",
            init={
                "conditions": {}
            },
            manual="assign_condition_result_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="conditions",
                                name="Conditions",
                                description="Please provide key-value pairs, where key is a path to some field in "
                                            "profile, and value is a condition that after being resolved the result "
                                            "will be assigned to profile field. "
                                            "(e.g. profile@consents.marketing-consent: "
                                            "profile@consents.marketing EXISTS) Every key must start with 'profile@'.",
                                component=FormComponent(type="keyValueList", props={
                                    "label": "Value",
                                    "defaultKeySource": "profile",
                                    "lockKeySource": True
                                })
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Resolve conditions into profile fields',
            desc='This plugin resolves a set of conditions and assigns it to the profile fields.',
            icon='question',
            group=["Flow control"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload without any changes.")
                }
            )
        )
    )
