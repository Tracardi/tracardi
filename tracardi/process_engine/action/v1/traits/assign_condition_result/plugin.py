from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.plugin.domain.result import Result
from tracardi.process_engine.tql.condition import Condition
from tracardi.domain.profile import Profile


def validate(config: dict) -> Config:
    return Config(**config)


class AssignConditionResultPlugin(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
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
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
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
                                            "profile, and value is a condition whose result will be assigned to given "
                                            "field. (e.g. profile@consents.marketing-consent: "
                                            "profile@consents.marketing EXISTS) Every key must start with 'profile@'.",
                                component=FormComponent(type="keyValueList", props={"label": "Value"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Assign condition results',
            desc='Ends workflow.',
            icon='plugin',
            group=["Conditions"],
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
