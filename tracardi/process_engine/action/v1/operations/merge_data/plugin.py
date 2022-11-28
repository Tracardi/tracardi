from collections import defaultdict

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.process_engine.action.v1.operations.merge_data.model.configuration import Configuration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class MergeDataAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)

        source = dot[self.config.source]
        data = dot[self.config.data]

        if not isinstance(source, dict) or not isinstance(data, dict):
            return Result(port="error", value={
                "message": f"Source and data must be a dictionaries of key value pairs, expected: dict, got: "
                           f"Source field type: {type(source)}: Data field type: {type(data)}"
            })

        if self.config.connection == 'override':
            for param in source:
                if param in data:
                    source[param] = data[param]

            return Result(port="true", value={"override_data": source})

        elif self.config.connection == 'merge':
            merged_data = {**source, **data}
            for k, v in merged_data.items():
                if k in source and k in data:
                    merged_data[k] = [v, source[k]]

            return Result(port='true', value={"merged_data": merged_data})

        else:
            return Result(port='error', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=MergeDataAction.__name__,
            inputs=["payload"],
            outputs=["true", "error"],
            version='0.7.4',
            license="MIT",
            author="Mateusz Zitaruk",
            init={
                "source": '',
                "data": "",
                "connection": None
            },
            manual="marge_data_action",
            form=Form(
                groups=[
                    FormGroup(
                        name='Merge data action configuration',
                        fields=[
                            FormField(
                                id='source',
                                name='Input data source.',
                                description='Please select a data source that you want to combine.',
                                component=FormComponent(type='dotPath',
                                                        props={
                                                            'label': 'Payload field',
                                                            "defaultSourceValue": "payload"
                                                        })
                            ),
                            FormField(
                                id='data',
                                name='Input data',
                                description='Please select a data that you want to combine with your source data.',
                                component=FormComponent(type='dotPath',
                                                        props={
                                                            'label': 'Payload field',
                                                            "defaultSourceValue": "payload"
                                                        })
                            ),
                            FormField(
                                id="connection",
                                name="Connection",
                                description="Choose method how to combine the data.",
                                component=FormComponent(
                                    type="select",
                                    props={
                                        "label": "Connection",
                                        "items": {
                                            "merge": "merge",
                                            "override": "override",
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
            name='Merge data',
            desc='This plugin combine data from two data schemas.',
            icon='exists',
            group=["Data Processing"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"true": PortDoc(desc="This port returns result of combination."),
                         "error":
                             PortDoc(desc="This port returns payload if field doesn't have correct data type.")
                         }
            )
        )
    )
