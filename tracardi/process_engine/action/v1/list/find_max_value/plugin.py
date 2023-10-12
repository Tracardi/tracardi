from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from pydantic import BaseModel

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc


class Configuration(BaseModel):
    source: str
    operation: str = 'max'


def validate(config: dict):
    return Configuration(**config)


class FindMaxValuePlugin(ActionRunner):
    config: Configuration

    async def set_up(self, config):
        self.config = validate(config)

    async def run(self, payload: dict, in_edge=None):
        try:
            dot = self._get_dot_accessor(payload)
            source_data = dot[self.config.source]

            if not isinstance(source_data, dict):
                raise ValueError("Source data is not a dictionary.")

            if not all(isinstance(value, (int, float)) for value in source_data.values()):
                raise ValueError("Not all values in the dictionary are numeric.")

            if self.config.operation == 'max':
                key = max(source_data, key=source_data.get)
            else:
                key = min(source_data, key=source_data.get)

            value = source_data[key]

            return Result(port='result', value={"key": key, "value": value})

        except Exception as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        spec=Spec(
            module=__name__,
            className=FindMaxValuePlugin.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "source": "",
                "operation": "max"
            },
            manual='list/find_max_value',
            form=Form(groups=[
                FormGroup(
                    name="Plugin Configuration",
                    fields=[
                        FormField(
                            id="source",
                            name="Source Path",
                            description="Dot-notation path to internal data",
                            component=FormComponent(type="dotPath", props={"label": "Source Path"})
                        ),
                        FormField(
                            id="operation",
                            name="Min/Max",
                            description="Select what value you would like to find.",
                            component=FormComponent(type="select", props={
                                "label": "Min/Max",
                                "items": {
                                    "min": "Min",
                                    "max": "Max"
                                }
                            })
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name="Max/Min Value",
            desc='This plugin returns the key with the maximum/minimum numeric value.',
            group=["Data Analysis"],
            documentation=Documentation(
                inputs={"payload": PortDoc(desc="Input payload.")},
                outputs={
                    "result": PortDoc(desc="The key with the maximum or minimum numeric value."),
                    "error": PortDoc(desc="An error message in case of an issue.")
                }
            )
        )
    )
