import json
from json import JSONDecodeError
from pydantic import field_validator
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.wf.domain.flow_graph import FlowGraph


class Configuration(PluginConfig):
    key: str
    body: str = ""
    default: bool = True

    @field_validator("key")
    @classmethod
    def key_may_not_be_empty(cls, value):
        if not value:
            raise ValueError("Key may not be empty")
        return value.replace(" ", "_").lower()

    @field_validator("body")
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
        json.loads(config.body)
    except JSONDecodeError as e:
        raise ValueError(str(e))

    return config


class CreateResponseAction(ActionRunner):

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

        output = json.loads(self.config.body)
        result = template.reshape(reshape_template=output)

        flow = self.flow  # type: FlowGraph
        flow.response[self.config.key] = result

        return Result(port="payload", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='CreateResponseAction',
            inputs=["payload"],
            outputs=['payload'],
            init={"key": "", "body": "{}", "default": True},
            form=Form(groups=[
                FormGroup(
                    name="Create response object",
                    fields=[
                        FormField(
                            id="key",
                            name="Response key name",
                            description="Type response key name. This is any non-spaced string that will identify the "
                                        "response data, e.g. user_name",
                            component=FormComponent(type="text", props={"label": "Key"})
                        ),
                        FormField(
                            id="body",
                            name="Response object",
                            description="Provide object as JSON to be injected into response and returned "
                                        "on output port.",
                            component=FormComponent(type="json", props={"label": "Response object"})
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
            manual="create_response_action",
            version='0.7.2',
            license="MIT + CC",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Create response',
            desc='Creates new response from provided data. Configuration defines where the data should be copied.',
            icon='json',
            group=["Data processing"],
            tags=['reshape', 'create', 'data', 'new'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns new payload the same as response.")
                }
            )
        )
    )
