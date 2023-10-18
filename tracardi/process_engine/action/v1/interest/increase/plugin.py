from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.wrappers import lock_for_profile_update
from ..config import Configuration


def validate(config: dict):
    return Configuration(**config)


class IncreaseInterestAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    @lock_for_profile_update
    async def run(self, payload: dict, in_edge=None) -> Result:

        if not isinstance(self.profile, Profile):
            if self.event.metadata.profile_less is True:
                msg = "Can not increase profile interest in profile less events."
                self.console.warning(msg)
            else:
                msg = "Can not increase interests to empty profile."
                self.console.error(msg)

            return Result(value={"message": msg}, port="error")

        self.profile.increase_interest(self.config.interest, float(self.config.value))
        self.profile.operation.update = True

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=IncreaseInterestAction.__name__,
            inputs=["payload"],
            outputs=['payload', 'error'],
            init={
                "interest": "",
                "value": "1.0"
            },
            form=Form(groups=[
                FormGroup(
                    name="Interest",
                    fields=[
                        FormField(
                            id="interest",
                            name="Interest name",
                            description="Please type interest name.",
                            component=FormComponent(type="text", props={"label": "Interest name"})
                        ),
                        FormField(
                            id="value",
                            name="Interest value",
                            description="Enter the value by which the interest needs to be raised.",
                            component=FormComponent(type="text", props={"label": "Interest value"})
                        )
                    ]
                )]
            ),
            version='0.8.0',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Increase interest',
            desc='Increases interest in profile and returns payload.',
            icon='plus',
            group=["Segmentation"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns object received by plugin in input."),
                    "error": PortDoc(desc="This port error message")
                }
            )
        )
    )
