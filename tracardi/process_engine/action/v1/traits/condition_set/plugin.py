from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.process_engine.tql.condition import Condition
from .model.config import Config
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class ConditionSetPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        condition = Condition()
        dot = self._get_dot_accessor(payload)

        conditions = {}
        for key, value in self.config.conditions.items():
            conditions[key] = await condition.evaluate(value, dot)

        return Result(port='result', value=conditions)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ConditionSetPlugin',
            inputs=["payload"],
            outputs=["result"],
            version='0.6.2.1',
            license="MIT",
            author="Daniel Demedziuk",
            init={
                'conditions': {}
            },
            manual="condition_set_action",
            form=Form(
                groups=[
                    FormGroup(
                        name='Plugin configuration',
                        fields=[
                            FormField(
                                id='conditions',
                                name='Conditions to evaluate',
                                description='Provide key - value pairs where key is your custom name for a condition and value is a condition to evaluate (e.g. profile@consents.marketing EXISTS).',
                                component=FormComponent(
                                    type='keyValueList',
                                    props={
                                        'label': 'condition'
                                    }
                                )
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Resolve conditions',
            desc='That plugin creates an object with results from resolved condition set.',
            icon='if',
            group=["Data processing"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns object with evaluated conditions.")
                }
            )
        )
    )