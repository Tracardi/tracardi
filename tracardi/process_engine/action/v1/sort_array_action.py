from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class SortConfig(PluginConfig):
    data: str
    direction: str

    @field_validator("data")
    @classmethod
    def must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("data is empty")
        return value

    @field_validator("direction")
    @classmethod
    def has_correct_direction(cls, value):
        if value not in ("asc", "desc"):
            raise ValueError("direction is not \"asc\" or \"desc\"")
        return value


def validate(config: dict):
    return SortConfig(**config)


class SortArrayAction(ActionRunner):
    config: SortConfig

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        reverse = True if self.config.direction == "desc" else False
        dot = self._get_dot_accessor(payload)
        try:
            data = dot[self.config.data]
        except KeyError as e:
            return Result(port="error", value={
                "message": str(e)
            })

        if isinstance(data, list):
            array = sorted(data, reverse=reverse)
            return Result(port="result", value=array)

        return Result(port="error", value={
            "message": f"Referenced {self.config.data} is not an array."
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module=__name__,
            className=SortArrayAction.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            manual="sort_array_action",
            init={
                "data": "",
                "direction": "asc",
            },
            version='0.7.3',
            license="MIT + CC",
            author="Tanay PrabhuDesai",
            form=Form(
                groups=[
                    FormGroup(
                        name="Sort array plugin configuration",
                        fields=[
                            FormField(
                                id="data",
                                name="Reference the data that you want to sort",
                                component=FormComponent(
                                    type="dotPath",
                                    props={
                                        "label": "Data",
                                        "defaultSourceValue": "event",
                                    }
                                ),
                            ),
                            FormField(
                                id="direction",
                                name="Direction of the sorting.",
                                component=FormComponent(
                                    type="select",
                                    props={
                                        "label": "Direction",
                                        "defaultSourceValue": "event",
                                        "items": {
                                            "asc": "Ascending",
                                            "desc": "Descending",
                                        }
                                    }
                                ),
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Sort list',
            desc='Plugin that sorts (ascending, descending) a referenced array/list.',
            keywords=['sort', 'array'],
            icon='sort',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object")
                },
                outputs={
                    "result": PortDoc(desc="Returns the sorted list/array")
                }
            ),
        )
    )
