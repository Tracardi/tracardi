from pydantic import validator

from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(PluginConfig):
    direction: str
    data: str

    @validator("direction")
    def if_order_is_empty(cls, value):
        if value == "":
            raise ValueError("Direction cannot be empty")
        return value

    @validator("direction")
    def if_order_has_valid_value(cls, value):
        if value == "asc" or value == "desc":
            return value
        raise ValueError("Direction has invalid value. Possible values are: \"asc\" or \"desc\".")

    @validator("data")
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
        dictionary_to_sort = dot[self.config.data]

        sorted_tuple_list = []
        is_desc = self.config.direction == "desc"
        for i in sorted(dictionary_to_sort, key=dictionary_to_sort.get, reverse=is_desc):
            sorted_tuple_list.append(tuple([i, dictionary_to_sort[i]]))
        return Result(port="payload", value={"result": sorted_tuple_list})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SortedDictAction',
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.3',
            license="MIT",
            author="Sameer Kavthekar",
            init={
                "data": "",
                "direction": ""
            },
            manual="sorted_dict_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Dictionary Sort plugin configuration",
                        fields=[
                            FormField(
                                id="data",
                                name="data",
                                description="The referenced dictionary that has to be sorted",
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
                                name="direction",
                                description="The order in which the dictionary is sorted",
                                component=FormComponent(
                                    type="select",
                                    props={
                                        "label": "direction",
                                        "items": {
                                            "asc": "Ascending",
                                            "desc": "Descending"
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
            name='Sort Referenced Dictionary',
            desc='Sorts the referenced dictionary and returns it as a list of tuples of key and value.',
            icon='question',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"payload": PortDoc(desc="This port returns the ordered list of tuples as key and value")}
            )
        )
    )
