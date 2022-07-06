from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner, JoinSettings
from tracardi.service.wf.domain.edge import Edge
from .model.config import Config
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class JoinPayloads(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)
        self.join = JoinSettings(
            merge=True,
            template=self.config.reshape,
            default=self.config.default
        )

    async def run(self, payload: dict, in_edge: Edge = None) -> Result:
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='JoinPayloads',
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "reshape": "{}",
                "default": True
            },
            manual="memory/join_output_payloads",
            form=Form(
                groups=[
                    FormGroup(
                        name="Join payloads settings",
                        fields=[
                            FormField(
                                id="reshape",
                                name="Reshape output payload",
                                description="Type transformation JSON to reshape the output payload",
                                component=FormComponent(type="json", props={"label": "Transformation object"})
                            ),
                            FormField(
                                id="default",
                                name="Missing values equal null",
                                description="Values that are missing will become null",
                                component=FormComponent(type="bool",
                                                        props={"label": "Make missing values equal to null"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Join',
            desc='Joins input data into one payload.',
            tags=['memory', 'join', "payload"],
            type="startNode",
            icon='flow',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload.")
                }
            )
        )
    )
