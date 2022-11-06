from pydantic import validator
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
        try:
            dot_notation = f"memory@{self.config.memory_key}"
            dot = self._get_dot_accessor(payload)

            return Result(value={"segments":dot[dot_notation]}, port="result")
        except KeyError as e:
            return Result(value={"message": str(e)}, port="error")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=MemorizeSegmentAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
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
                            description="You can recall segments from different stages of a workflow. "
                                        "To read/recall the proper segment you should provide the same a key "
                                        "that you set when memorizing the profile segments. Default is: "
                                        "profile.segments, but you can use like profile.segments.stage1, etc.",
                            component=FormComponent(type="text", props={"label": "memory_key"})
                        )
                    ]
                )]
            ),
            # manual="recall_segment_action"
        ),
        metadata=MetaData(
            name='Recall segment',
            desc='Loads memorized profile segments into output payload.',
            icon='segment',
            group=["Segmentation"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns memorized segments."),
                    "error": PortDoc(desc="This port returns error message if segments could no tbe found.")
                }
            ),
            pro=True
        )
    )
