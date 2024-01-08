from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class ArrayReducer(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        array_to_reduce = dot[self.config.array]
        result = {"counts": {}, "max": None, "min": None, "total": len(array_to_reduce)}

        try:
            for element in array_to_reduce:
                if str(element) not in result["counts"]:
                    result["counts"][str(element)] = 0
                result["counts"][str(element)] += 1

            result["max"] = max(result["counts"], key=result["counts"].get)
            result["min"] = min(result["counts"], key=result["counts"].get)

            return Result(port="result", value=result)

        except Exception as e:
            return Result(port="error", value={"error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ArrayReducer',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.6.2',
            license="MIT + CC",
            author="Dawid Kruk",
            init={
                "array": None
            },
            manual="reduce_array_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="array",
                                name="Path to array",
                                description="Please provide a path to an array that you want to reduce.",
                                component=FormComponent(type="dotPath", props={"label": "Array", "defaultSourceValue": "event"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Reduce array',
            desc='Reduces given array.',
            icon='array',
            group=["Operations"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns result of array reduction."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
