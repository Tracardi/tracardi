from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    PortDoc, Documentation


class Configuration(PluginConfig):
    set1: str
    set2: str
    operation: str


def validate(config: dict):
    return Configuration(**config)


class SetOperationPlugin(ActionRunner):
    config: Configuration

    async def set_up(self, config):
        self.config = validate(config)

    async def run(self, payload, in_edge=None):
        dot = self._get_dot_accessor(payload)
        set1 = set(dot[self.config.set1])
        set2 = set(dot[self.config.set2])

        operation = self.config.operation.lower()

        try:
            if operation == "intersection":
                result_set = list(set1.intersection(set2))
            elif operation == "union":
                result_set = list(set1.union(set2))
            elif operation == "difference":
                result_set = list(set1.difference(set2))
            elif operation == "symmetric_difference":
                result_set = list(set1.symmetric_difference(set2))
            elif operation == "is_subset":
                result_set = set1.issubset(set2)
            elif operation == "is_superset":
                result_set = set1.issuperset(set2)
            else:
                raise ValueError("Invalid operation specified.")

            return Result(port="result", value={"result": result_set})

        except Exception as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        spec=Spec(
            module=__name__,
            className=SetOperationPlugin.__name__,
            init={
                "set1": "",
                "set2": "",
                "operation": "intersection"
            },
            form=Form(groups=[
                FormGroup(
                    name="Plugin Configuration",
                    fields=[
                        FormField(
                            id="set1",
                            name="Set 1",
                            description="Reference to the first set data.",
                            component=FormComponent(type="dotPath", props={"label": "Set 1"})
                        ),
                        FormField(
                            id="set2",
                            name="Set 2",
                            description="Reference to the second set data.",
                            component=FormComponent(type="dotPath", props={"label": "Set 2"})
                        ),
                        FormField(
                            id="operation",
                            name="Set Operation",
                            description="Select the set operation to perform.",
                            component=FormComponent(type="select", props={
                                "label": "Set Operation",
                                "items": {
                                    "intersection": "Intersection",
                                    "union": "Union",
                                    "difference": "Difference",
                                    "symmetric_difference": "Symmetric Difference",
                                    "is_subset": "Is Subset",
                                    "is_superset": "Is Superset"
                                }
                            })
                        )
                    ]
                ),
            ]),
            inputs=['payload'],
            outputs=["result", "error"],
            version='8.2.0',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="list/sets_operations"
        ),
        metadata=MetaData(
            name="Operations on sets",
            desc='Perform some operations on two sets of data. Operations like intersection, union, etc.',
            group=["Data Processing"],
            documentation=Documentation(
                inputs={"payload": PortDoc(desc="Input payload.")},
                outputs={
                    "result": PortDoc(desc="Result of the set operation."),
                    "error": PortDoc(desc="Error message if an exception occurs.")
                }
            )
        )
    )
