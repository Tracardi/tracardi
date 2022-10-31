from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.domain.event import Event
from tracardi.domain.session import Session
from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.process_engine.tql.equation import MathEquation


class SortConfig(PluginConfig):
    data: str
    direction: str

    @validator("data")
    def must_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("data is empty")
        return value

    @validator("direction")
    def has_correct_direction(cls, value):
        if value not in ("asc", "desc"):
            raise ValueError("direction is not \"asc\" or \"desc\"")
        return value


def validate(config: dict):
    return SortConfig(**config)


class SortAction(ActionRunner):
    config: SortConfig

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        reverse = True if self.config.direction == "desc" else False
        dot = self._get_dot_accessor(payload)
        data = dot[self.config.data]
        array = sorted(data, reverse=reverse)
        return Result(port="sorted_array", value=array)


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module=__name__,
            className=SortAction.__name__,
            inputs=["payload"],
            outputs=["sorted_array"],
            manual="sort_action",
            init={
                "data": "",
                "direction": "asc",
            },
            version='0.0.0.1',
            license="MIT",
            author="Tanay PrabhuDesai",
            form=Form(
                groups=[
                    FormGroup(
                        name="Sort plugin configuration",
                        fields=[
                            FormField(
                                id="data",
                                name="Type dotted path from the payload that you want to sort",
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
                                name="Direction of the sorting that you want to be done",
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
            name='SortAction',
            desc='Plugin that sorts (ascending, descending) a referenced array in plugin config',
            keywords=['sort'],
            group=["Flow Control"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object")
                },
                outputs={
                    "sorted_array": PortDoc(desc="Returns the sorted array")
                }
            ),
        )
    )
