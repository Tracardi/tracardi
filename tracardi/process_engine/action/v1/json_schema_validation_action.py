from tracardi.service.console_log import ConsoleLog
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from pydantic import validator
from typing import Dict, Union
from tracardi.exceptions.exception import EventValidationException
from tracardi.domain.event_validator import EventValidator, ValidationSchema
import jsonschema
import json
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.tracker_event_validator import EventsValidationHandler


class Config(PluginConfig):
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

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        payload_validator = EventValidator(
            validation=ValidationSchema(json_schema=self.config.validation_schema),
            event_type="no-type",
            name="validation",
            id="1",
            tags=[]
        )

        try:
            v = EventsValidationHandler(dot, ConsoleLog())
            result = v.validate_with_multiple_schemas([payload_validator])
            if result:
                return Result(port="true", value=payload)
            return Result(port="false", value=payload)
        except EventValidationException:
            return Result(port="error", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SchemaValidator',
            inputs=["payload"],
            outputs=["true", "false", "error"],
            version='0.7.4',
            license="MIT",
            author="Dawid Kruk, Risto Kowaczewski",
            manual="validate_with_json_schema_action",
            init={
                "validation_schema": {}
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="JSON Schema Validation Configuration",
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
            name='JSON schema validator',
            desc='Validates objects using provided JSON validation schema.',
            icon='ok',
            group=["Validators"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "true": PortDoc(desc="This port returns payload if it passes defined validation."),
                    "false": PortDoc(desc="This port returns payload if it does not pass defined validation."),
                    "error": PortDoc(desc="This port returns payload if it does not pass defined validation "
                                          "due to an error in validation schema.")
                }
            )
        )
    )
