from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.action_runner import ActionRunner
from pydantic import BaseModel, validator
from typing import Dict, Union
from tracardi.service.event_validator import validate as validate_with_schema
from tracardi.exceptions.exception import EventValidationException
from tracardi.domain.event_payload_validator import EventPayloadValidator
import jsonschema
import json


class Config(BaseModel):
    validation_schema: Union[str, Dict[str, Dict]]

    @validator("validation_schema")
    def validate_config_schema(cls, v):
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Given JSON is invalid.")

        for value in v.values():
            try:
                jsonschema.Draft202012Validator.check_schema(value)
            except jsonschema.SchemaError:
                raise ValueError(f"Given validation JSON-schema is invalid.")
        return v


def validate(config: dict) -> Config:
    return Config(**config)


class SchemaValidator(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        payload_validator = EventPayloadValidator(
            validation=self.config.validation_schema,
            event_type="no-type",
            name="validation",
            enabled=True,
            tags=[]
        )

        try:
            validate_with_schema(dot, payload_validator)
            return Result(port="OK", value=payload)
        except EventValidationException:
            return Result(port="ERROR", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SchemaValidator',
            inputs=["payload"],
            outputs=["OK", "ERROR"],
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            manual="validate_with_json_schema_action",
            init={
                "validation_schema": {}
            },
            form=Form(
                name="Plugin configuration",
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="validation_schema",
                                name="JSON validation schema",
                                description="Please provide a JSON validation schema that you want to validate data "
                                            "with.",
                                component=FormComponent(type="json", props={"label": "Schema"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Validate with JSON schema',
            desc='Validates objects using provided JSON validation schema.',
            type='flowNode',
            icon='plugin',
            group=["Data processing"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "OK": PortDoc(desc="This port returns payload if it passes defined validation."),
                    "ERROR": PortDoc(desc="This port returns payload if it does not pass defined validation.")
                }
            )
        )
    )
