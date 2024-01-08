from tracardi.service.utils.date import now_in_utc

from pydantic import field_validator

from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
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


class DeleteSegmentAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if isinstance(self.profile, Profile):
            dot = self._get_dot_accessor(payload)
            profile = Profile(**dot.profile)
            if self.config.segment in self.profile.segments:
                profile.metadata.time.segmentation = now_in_utc()

                profile.segments = list(set(profile.segments))
                profile.segments.remove(self.config.segment)
            self.profile.replace(profile)
        else:
            if self.event.metadata.profile_less is True:
                self.console.warning("Can not segment profile when processing profile less events.")
            else:
                self.console.error("Can not segment profile. Profile is empty.")

        return Result(value=payload, port="payload")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='DeleteSegmentAction',
            inputs=["payload"],
            outputs=["payload"],
            version="0.8.1",
            author="Risto Kowaczewski",
            manual="segmentation/delete_segment_action",
            init={
                "segment": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Segment",
                    fields=[
                        FormField(
                            id="segment",
                            name="Segment name",
                            description="Please type segment name.",
                            component=FormComponent(type="text", props={"label": "Segment name"})
                        )
                    ]
                )]
            ),
        ),
        metadata=MetaData(
            name='Delete segment',
            desc='Deletes profile from segment.',
            keywords=['remove', 'unset'],
            icon='segment',
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
