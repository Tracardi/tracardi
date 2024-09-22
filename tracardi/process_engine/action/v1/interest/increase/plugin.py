from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from ..config import Configuration
from ..utils import is_valid_string


def validate(config: dict):
    return Configuration(**config)


class IncreaseInterestAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        if not isinstance(self.profile, Profile):
            if self.event.metadata.profile_less is True:
                msg = "Can not increase profile interest in profile less events."
                self.console.warning(msg)
            else:
                msg = "Can not increase interests to empty profile."
                self.console.error(msg)

            return Result(value={"message": msg}, port="error")

        dot = self._get_dot_accessor(payload)
        interest_key = dot[self.config.interest]

        if isinstance(interest_key, list):
            interests_keys = interest_key
        else:
            if not is_valid_string(interest_key):
                message = (
                    f"Invalid interest name. Expected alpha-numeric string without spaces, got `{interest_key}`. "
                    f"Interest name must be an alpha-numeric string without spaces. Hyphen and dashes are allowed.")

                self.console.error(message)

                return Result(port="error", value={"message": message})

            interests_keys = interest_key.split(',')

        for interest_key in interests_keys:

            if not is_valid_string(interest_key):
                message = (
                    f"Invalid interest name. Expected alpha-numeric string without spaces, got `{interest_key}`. "
                    f"Interest name must be an alpha-numeric string without spaces. Hyphen and dashes are allowed.")
                self.console.error(message)
                continue

            self.profile.increase_interest(interest_key, float(self.config.value))
        self.profile.set_updated()

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
                            description="Please type interest name. You can reference the name form payload, or event properties if needed.",
                            component=FormComponent(type="dotPath", props={"label": "Interest name"})
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
            version='1.0.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="increase_interest"
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
