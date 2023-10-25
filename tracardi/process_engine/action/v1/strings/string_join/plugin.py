from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class JoinAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        data_to_join = dot[self.config.string]

        if not isinstance(data_to_join, list):
            raise ValueError('Referenced data must be an array')

        result = self.config.delimiter.join(data_to_join)
        return Result(port="payload", value={"result": result})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.strings.string_join.plugin',
            className='JoinAction',
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.3',
            license="MIT + CC",
            author="Yusuke Kohatsu",
            manual="string_join_action",
            init={
                "string": None,
                "delimiter": ','
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="string",
                            name="List of string",
                            description="Select source and path to string that references list data.",
                            component=FormComponent(type="dotPath", props={"defaultSourceValue": "event"})
                        ),
                        FormField(
                            id="delimiter",
                            name="Delimiter",
                            description="Type delimiter. It will be used to join the element stored in the list.",
                            component=FormComponent(type="text", props={"label": "delimiter"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name="Join string list",
            desc='It joins each element in the list by given delimiter.',
            icon='uppercase',
            group=["String"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns joined array as string.")
                }
            ),
        )
    )
