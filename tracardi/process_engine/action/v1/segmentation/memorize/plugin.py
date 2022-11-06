from pydantic import validator

from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormComponent, FormField
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Configuration(PluginConfig):
    memory_key: str

    @validator("memory_key")
    def is_not_empty(cls, value):
        if value == "":
            raise ValueError("Segment memory key cannot be empty")
        return value


def validate(config: dict):
    return Configuration(**config)


class MemorizeSegmentAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if not isinstance(self.profile, Profile):
            if self.event.metadata.profile_less is True:
                self.console.warning("Can not memorize segment of profile when there is no profile (profileless event.")
            else:
                self.console.error("Can not memorize segment profile. Profile is empty.")
        else:
            dot_notation = f"memory@{self.config.memory_key}"
            dot = self._get_dot_accessor(payload)
            dot[dot_notation] = self.profile.segments

        return Result(value=payload, port="payload")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=MemorizeSegmentAction.__name__,
            inputs=["payload"],
            outputs=["payload"],
            version="0.7.3",
            author="Risto Kowaczewski",
            license="Tracardi Pro License",
            init={
                "memory_key": "profile.segments"
            },
            form=Form(groups=[
                FormGroup(
                    name="Segment",
                    fields=[
                        FormField(
                            id="memory_key",
                            name="Memory key",
                            description="You can memorize segments may times and on different stages of a workflow. "
                                        "To read/recall the proper segment you should define a key (this is like a pointer) "
                                        "that you will use to read the memorized profile segments. Default is: "
                                        "profile.segments, but you can use like profile.segments.stage1, etc.",
                            component=FormComponent(type="text", props={"label": "memory_key"})
                        )
                    ]
                )]
            ),
            # manual="memorize_segment_action"
        ),
        metadata=MetaData(
            name='Memorize segment',
            desc='Memorize profile segments in workflow memory.',
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
            ),
            pro=True
        )
    )
