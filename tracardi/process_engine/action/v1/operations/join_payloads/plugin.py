from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner, JoinSettings, ReshapeTemplate
from tracardi.service.wf.domain.edge import Edge
from .model.config import Config
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class JoinPayloads(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)
        self.join = JoinSettings(
            merge=True,
            reshape={  # Reshape definition for payload output port
                "payload": ReshapeTemplate(
                    template=self.config.reshape,
                    default=self.config.default)
            },
            type=self.config.type
        )

    async def run(self, payload: dict, in_edge: Edge = None) -> Result:
        # Return joined input payloads. Payloads can be transformed by the `Reshape output payload` schema.
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
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "reshape": "{}",
                "default": True,
                "type": "dict"
            },
            manual="join_output_payloads",
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
                                id="type",
                                name="Type of join",
                                description="Select type of collection. Type of `Dictionary` uses the connection names "
                                            "as keys in dictionary.",
                                component=FormComponent(type="select", props={"label": "Name", "items": {
                                    "list": "List",
                                    "dict": "Dictionary"
                                }})
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
            purpose=['collection', 'segmentation'],
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
