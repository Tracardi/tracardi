from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.session import Session
from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.process_engine.tql.equation import MathEquation


class CalculatorConfig(PluginConfig):
    calc_dsl: str

    @field_validator("calc_dsl")
    @classmethod
    def must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Calculations are empty.")
        return value


def validate(config: dict):
    return CalculatorConfig(**config)


class CalculatorAction(ActionRunner):
    config: CalculatorConfig

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        calc_lines = [line.strip() for line in self.config.calc_dsl.split("\n")]

        dot = self._get_dot_accessor(payload)

        equation = MathEquation(dot)
        results = equation.evaluate(calc_lines)

        if self.event.metadata.profile_less is False:
            profile = Profile(**dot.profile)
            self.profile.replace(profile)

        if 'id' in dot.session:
            session = Session(**dot.session)
            self.session.replace(session)

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
            version='0.8.2',
            license="MIT + CC",
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
                                        "Example: profile@aux.counters.my_count = profile@aaux.visits + 1",
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
            purpose=['collection', 'segmentation'],
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
