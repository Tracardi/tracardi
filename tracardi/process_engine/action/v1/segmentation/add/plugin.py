from typing import List, Union

from pydantic import validator

from tracardi.domain.profile import Profile
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Configuration(PluginConfig):
    segment: Union[str, List[str]]

    @validator("segment")
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
                if not self.debug:
                    profile.operation.update = True
                else:
                    self.console.warning("Profile is not updated in debug mode.")

                try:
                    dot = self._get_dot_accessor(payload)
                    if isinstance(self.config.segment, list):
                        converter = DictTraverser(dot, include_none=False)
                        segments = converter.reshape(self.config.segment)
                        profile.segments += segments

                    elif isinstance(self.config.segment, str):
                        profile.segments.append(dot[self.config.segment])

                    else:
                        return Result(value={"message": "Not acceptable segmentation type. "
                                                        "Allowed type: string or list of strings"}, port="error")
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
            version="0.7.3",
            author="Risto Kowaczewski",
            init={
                "segment": ""
            },
            manual="segment_add_action"
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
