from tracardi.domain.profile import Profile
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from ..config import Configuration


def validate(config: dict):
    return Configuration(**config)


class AddInterestAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        if not isinstance(self.profile, Profile):
            if self.event.metadata.profile_less is True:
                msg = "Can not add interests profile when processing profile less events."
                self.console.warning("Can not add interests profile when processing profile less events.")
            else:
                msg = "Can not add interests to empty profile."
                self.console.error("Can not add interests to empty profile.")
            return Result(value={"message": msg}, port="error")

        dot = self._get_dot_accessor(payload)
        profile = Profile(**dot.profile)
        if self.config.interest not in self.profile.interests:
            profile.set_updated()

            try:
                dot = self._get_dot_accessor(payload)
                if isinstance(self.config.interest, list):
                    converter = DictTraverser(dot, include_none=False)
                    interests = converter.reshape(self.config.interest)

                elif isinstance(self.config.interest, str):
                    interests = [dot[self.config.interest]]

                else:
                    return Result(value={"message": "Not acceptable interest type. "
                                                    "Allowed type: string or list of strings"}, port="error")

                for interest in interests:
                    profile.interests[interest] = float(self.config.value)

            except KeyError as e:
                return Result(value={"message": str(e)}, port="error")

        self.profile.replace(profile)

        return Result(value=payload, port="payload")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=AddInterestAction.__name__,
            inputs=["payload"],
            outputs=["payload", "error"],
            version="0.8.0",
            author="Risto Kowaczewski",
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
                            description="Please type how do you value this interest.",
                            component=FormComponent(type="text", props={"label": "Interest value"})
                        )
                    ]
                )]
            ),
        ),
        metadata=MetaData(
            name='Add interest',
            desc='Adds interest to profile.',
            icon='interest',
            group=["Segmentation"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload.")

                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload."),
                    "error": PortDoc(desc="This port error message.")
                }
            )
        )
    )
