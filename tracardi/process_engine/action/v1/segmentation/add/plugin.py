from tracardi.process_engine.action.v1.segmentation.service.profile_segmentation_services import add_segment_to_profile
from tracardi.service.utils.date import now_in_utc

from typing import List, Union

from pydantic import field_validator

from tracardi.domain.profile import Profile
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Configuration(PluginConfig):
    segment: Union[str, List[str]]

    @field_validator("segment")
    @classmethod
    def is_not_empty(cls, value):
        if not value:
            raise ValueError("Segment cannot be empty")
        return value


def validate(config: dict):
    return Configuration(**config)


class AddSegmentAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if isinstance(self.profile, Profile):
            dot = self._get_dot_accessor(payload)
            profile = Profile(**dot.profile)
            if self.config.segment not in self.profile.segments:
                profile.metadata.time.segmentation = now_in_utc()

                try:
                    dot = self._get_dot_accessor(payload)
                    if isinstance(self.config.segment, (list, str)):
                        converter = DictTraverser(dot, include_none=False)
                        segments = converter.reshape(self.config.segment)
                        add_segment_to_profile(profile, segments)
                    else:
                        return Result(value={
                            "message": "Not acceptable segmentation type. "
                                       "Allowed type: string or list of strings"},
                            port="error")
                except KeyError as e:
                    return Result(value={"message": str(e)}, port="error")

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
            className='AddSegmentAction',
            inputs=["payload"],
            outputs=["payload", "error"],
            version="0.8.1",
            author="Risto Kowaczewski",
            manual="segmentation/add_segment_action",
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
                            component=FormComponent(type="dotPath", props={"label": "Segment name"})
                        )
                    ]
                )]
            ),
        ),
        metadata=MetaData(
            name='Add segment',
            desc='Adds segment to profile.',
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
