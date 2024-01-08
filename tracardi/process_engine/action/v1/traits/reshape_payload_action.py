import json
from json import JSONDecodeError
from pydantic import field_validator
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    value: str = ""
    default: bool = True

    @field_validator("value")
    @classmethod
    def validate_content(cls, value):
        try:
            if isinstance(value, dict):
                value = json.dumps(value)
            return value

        except JSONDecodeError as e:
            raise ValueError(str(e))


def validate(config: dict) -> Configuration:
    config = Configuration(**config)

    # Try parsing JSON just for validation purposes
    try:
        json.loads(config.value)
    except JSONDecodeError as e:
        raise ValueError(str(e))

    return config


class ReshapePayloadAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = Configuration(**init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if not isinstance(payload, dict):
            self.console.warning("Payload has to be an object.")

        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        if self.config.default is True:
            template = DictTraverser(dot, default=None)
        else:
            template = DictTraverser(dot)

        output = json.loads(self.config.value)

        try:
            result = template.reshape(reshape_template=output)
        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={"message": str(e)})

        if not isinstance(result, dict):
            message = "Result from this node is not an object/dictionary."
            return Result(port="error", value={"message": message})

        return Result(port="payload", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=ReshapePayloadAction.__name__,
            inputs=["payload"],
            outputs=['payload', 'error'],
            init={"value": "{}", "default": True},
            form=Form(groups=[
                FormGroup(
                    name="Create payload object",
                    fields=[
                        FormField(
                            id="value",
                            name="Object to inject",
                            description="Provide object as JSON to be injected into payload and returned "
                                        "on output port.",
                            component=FormComponent(type="json", props={"label": "object", "autocomplete": True})
                        ),
                        FormField(
                            id="default",
                            name="Missing values equal null",
                            description="Values that are missing will become null",
                            component=FormComponent(type="bool", props={"label": "Make missing values equal to null"})
                        )
                    ]
                ),
            ]),
            manual="reshape_payload_action",
            version='0.8.0',
            license="MIT + CC",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Inject payload',
            desc='Creates new payload from provided data. Configuration defines where the data should be copied.',
            icon='json',
            group=["Input/Output"],
            tags=['reshape', 'create', 'payload', 'data', 'make'],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns new payload,formed from given payload"
                                            " according to configuration.")
                }
            )
        )
    )
