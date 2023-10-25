from pydantic import field_validator

from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(PluginConfig):
    direction: str
    data: str
    sort_by: str

    @field_validator("direction")
    @classmethod
    def if_order_is_empty(cls, value):
        if value == "":
            raise ValueError("Direction cannot be empty")
        return value

    @field_validator("direction")
    @classmethod
    def if_order_has_valid_value(cls, value):
        if value == "asc" or value == "desc":
            return value
        raise ValueError("Direction has invalid value. Possible values are: \"asc\" or \"desc\".")

    @field_validator("sort_by")
    @classmethod
    def if_sprt_by_has_valid_value(cls, value):
        if value == "key" or value == "value":
            return value
        raise ValueError("Direction has invalid value.")

    @field_validator("data")
    @classmethod
    def if_data_is_empty(cls, value):
        if value == "":
            raise ValueError("Data cannot be empty")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class SortedDictAction(ActionRunner):
    config: Config

    async def set_up(self, config):
        self.config = validate(config)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        try:
            dictionary_to_sort = dot[self.config.data]
        except KeyError as e:
            return Result(port="error", value={
                "message": str(e)
            })

        if isinstance(dictionary_to_sort, dict):
            is_desc = self.config.direction == "desc"
            if self.config.sort_by == 'key':
                pos = 0
            else:
                pos = 1

            sorted_tuple_list = sorted(dictionary_to_sort.items(), key=lambda x: x[pos], reverse=is_desc)

            return Result(port="result", value={"result": sorted_tuple_list})

        return Result(port="error", value={
            "message": f"Referenced {self.config.data} is not a dictionary."
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SortedDictAction',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.7.3',
            license="MIT + CC",
            author="Sameer Kavthekar",
            init={
                "data": "",
                "direction": "asc",
                "sort_by": "key"
            },
            manual="sorted_dict_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Dictionary sorting configuration",
                        fields=[
                            FormField(
                                id="data",
                                name="Data to be sorted",
                                description="The dictionary that has to be sorted",
                                component=FormComponent(
                                    type="dotPath",
                                    props={
                                        "label": "Data to sort",
                                        "defaultSourceValue": "event"
                                    }
                                )
                            ),
                            FormField(
                                id="direction",
                                name="Sorting direction",
                                description="The order in which the dictionary is to be sorted",
                                component=FormComponent(
                                    type="select",
                                    props={
                                        "label": "Direction",
                                        "items": {
                                            "asc": "Ascending",
                                            "desc": "Descending"
                                        }
                                    }
                                )
                            ),
                            FormField(
                                id="sort_by",
                                name="Sort by",
                                description="Select the dictionary sort type: key or value",
                                component=FormComponent(
                                    type="select",
                                    props={
                                        "label": "Sort by",
                                        "items": {
                                            "key": "Key",
                                            "value": "Value"
                                        }
                                    }
                                )
                            )
                        ]
                    )
                ]
            )

        ),
        metadata=MetaData(
            name='Sort dictionary',
            desc='Sorts the referenced dictionary and returns it as a list of tuples of key and value.',
            icon='sort',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"payload": PortDoc(desc="This port returns the ordered list of tuples with keys and values")}
            )
        )
    )
