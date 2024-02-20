from pydantic import field_validator

from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormComponent, FormField
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Configuration(PluginConfig):
    segment: str

    @field_validator("segment")
    @classmethod
    def is_not_empty(cls, value):
        if value == "":
            raise ValueError("Segment cannot be empty")
        return value


def validate(config: dict):
    return Configuration(**config)


class HasSegmentAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if not isinstance(self.profile, Profile):
            if self.event.metadata.profile_less is True:
                self.console.warning("Can not check segment of profile when there is no profile (profileless event.")
            else:
                self.console.error("Can not check segment profile. Profile is empty.")
        else:
            if self.config.segment in self.profile.segments:
                return Result(port="True", value=payload)

        return Result(value=payload, port="False")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=HasSegmentAction.__name__,
            inputs=["payload"],
            outputs=["True", "False"],
            version="0.7.3",
            author="Risto Kowaczewski",
            init={
                "segment": ""
            },
            manual="segmentation/has_segment_action",
            form=Form(groups=[
                FormGroup(
                    name="Segment",
                    fields=[
                        FormField(
                            id="segment",
                            name="Profile segment to check",
                            component=FormComponent(type="text", props={"label": "Segment"})
                        )
                    ]
                )]
            ),
        ),
        metadata=MetaData(
            name='Has segment',
            desc='Checks if profile is in defined segment.',
            icon='segment',
            type="condNode",
            group=["Segmentation"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload.")
                }
            )
        )
    )
