from pydantic import BaseModel, validator
from tracardi.domain.event import Event
from tracardi.domain.session import Session
from tracardi.domain.profile import Profile
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi.process_engine.tql.equation import MathEquation


class CalculatorConfig(BaseModel):
    calc_dsl: str

    @validator("calc_dsl")
    def must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Calculations are empty.")
        return value


def validate(config: dict):
    return CalculatorConfig(**config)


class CalculatorAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload: dict):
        calc_lines = [line.strip() for line in self.config.calc_dsl.split("\n")]

        dot = self._get_dot_accessor(payload)

        equation = MathEquation(dot)
        results = equation.evaluate(calc_lines)

        if self.event.metadata.profile_less is False:
            profile = Profile(**dot.profile)
            self.profile.replace(profile)

        session = Session(**dot.session)
        self.session.replace(session)

        event = Event(**dot.event)
        self.event.replace(event)

        return Result(port="payload", value={
            "result": results[-1],
            "variables": equation.get_variables()
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.calculator_action',
            className='CalculatorAction',
            inputs=["payload"],
            outputs=["payload"],
            manual="calculator_action",
            init={
                "calc_dsl": ""
            },
            version='0.6.0.1',
            license="MIT",
            author="Risto Kowaczewski",
            form=Form(groups=[
                FormGroup(
                    name="Calculations",
                    description="Calculations are made in a simple domain specific language. "
                                "See documentation for details.",
                    fields=[
                        FormField(
                            id="calc_dsl",
                            name="Calculation equations",
                            description="One calculation per line. "
                                        "Example: profile@stats.counters.my_count = profile@stats.visits + 1",
                            component=FormComponent(type="textarea", props={"label": "Calculations"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Calculator',
            desc='Calculates new values. Adds, subtracts, divides, and multiplies values.',
            keywords=['math'],
            icon='calculator',
            group=["Data processing"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns result of calculations.")
                }
            )
        )
    )
