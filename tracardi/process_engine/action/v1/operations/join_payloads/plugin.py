from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.wf.domain.edge import Edge
from .model.config import Config
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class JoinPayloads(ActionRunner):

    def __init__(self, **kwargs):
        self.merge_out_payloads = True
        self.config = Config(**kwargs)

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
                "name": None,
                "type": "list"
            },
            manual="memory/join_output_payloads",
            form=Form(
                groups=[
                    FormGroup(
                        name="Payload memory collector configuration",
                        fields=[
                            FormField(
                                id="name",
                                name="Name of collection",
                                description="Please provide the name under which the collection will be saved.",
                                component=FormComponent(type="text", props={"label": "Name"})
                            ),
                            FormField(
                                id="type",
                                name="Type of collection",
                                description="Select type of collection. Type of `Dictionary` requires named connections "
                                            "in the workflow.",
                                component=FormComponent(type="select", props={"label": "Name", "items": {
                                    "list": "List",
                                    "dict": "Dictionary"
                                }})
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
