from tracardi.service.utils.date import now_in_utc

from pydantic import field_validator

from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Configuration(PluginConfig):
    from_segment: str
    to_segment: str

    @field_validator("from_segment")
    @classmethod
    def is_not_empty_from(cls, value):
        if value == "":
            raise ValueError("Segment cannot be empty")
        return value

    @field_validator("to_segment")
    @classmethod
    def is_not_empty_to(cls, value):
        if value == "":
            raise ValueError("Segment cannot be empty")
        return value


def validate(config: dict):
    return Configuration(**config)


class MoveSegmentAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if isinstance(self.profile, Profile):
            dot = self._get_dot_accessor(payload)
            profile = Profile(**dot.profile)
            profile.segments = list(set(profile.segments))
            if self.config.from_segment in profile.segments:
                profile.segments.remove(self.config.from_segment)
            if self.config.to_segment not in profile.segments:
                profile.segments.append(self.config.to_segment)
            profile.metadata.time.segmentation = now_in_utc()
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
            className=MoveSegmentAction.__name__,
            inputs=["payload"],
            outputs=["payload"],
            version="0.8.1",
            author="Risto Kowaczewski",
            manual="segmentation/move_segment_action",
            init={
                "from_segment": "",
                "to_segment": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Segment to move from",
                    fields=[
                        FormField(
                            id="from_segment",
                            name="Move from segment",
                            description="Please type segment name.",
                            component=FormComponent(type="text", props={"label": "Source segment"})
                        )
                    ]
                ),
                FormGroup(
                    name="Segment to move to",
                    fields=[
                        FormField(
                            id="to_segment",
                            name="Move to segment",
                            description="Please type segment name.",
                            component=FormComponent(type="text", props={"label": "Target segment"})
                        )
                    ]
                )
            ]
            ),
        ),
        metadata=MetaData(
            name='Move segment',
            desc='Moves profile from one segment to other segment.',
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
