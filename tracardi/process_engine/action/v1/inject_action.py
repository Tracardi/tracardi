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
    value: str = "{}"
    destination: str = "payload"

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


class InjectAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = Configuration(**init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        if self.debug is True:
            self.event.metadata.debug = True

        converter = DictTraverser(self._get_dot_accessor(payload))

        try:
            output = json.loads(self.config.value)
        except JSONDecodeError as e:
            raise ValueError(str(e))

        inject = converter.reshape(output)
        if self.config.destination == 'event-properties':
            self.event.properties = inject
        elif self.config.destination == 'profile-pii':
            self.profile.data.pii = inject
        elif self.config.destination == 'profile-traits':
            self.profile.traits = inject
        elif self.config.destination == 'profile-interests':
            self.profile.interests = inject
        elif self.config.destination == 'profile-counters':
            self.profile.stats.counters = inject
        elif self.config.destination == 'profile-consents':
            self.profile.consents = inject
        elif self.config.destination == 'session-context':
            self.session.context = inject
        elif self.config.destination == 'payload':
            return Result(value=inject, port="payload")
        return Result(value={}, port="payload")


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=True,
        spec=Spec(
            module=__name__,
            className=InjectAction.__name__,
            inputs=[],
            outputs=["payload"],
            init={"value": "{}", "destination": "payload"},
            form=Form(groups=[
                FormGroup(
                    name="Create payload object",
                    fields=[
                        FormField(
                            id="value",
                            name="Object to inject",
                            description="Type object as JSON to be injected into payload and returned "
                                        "on output port.",
                            component=FormComponent(type="json", props={"label": "object"})
                        ),
                        FormField(
                            id="destination",
                            name="Inject data into",
                            description="Select where the data should be injected.",
                            component=FormComponent(type="select", props={"label": "Destination", "items":{
                                'event-properties': "Event Properties",
                                'payload': "Payload",
                                'profile-pii': "Profile PII",
                                'profile-traits': "Profile Traits",
                                'profile-interests': "Profile Interests",
                                'profile-counters': "Profile Counters",
                                'profile-consents': "Profile Consents",
                                'session-context': "Session Context"
                            }})
                        )
                    ]
                ),
            ]),
            manual='inject_action',
            version='0.8.1',
            license="MIT + CC",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Inject',
            type="startNode",
            desc='Injects data into selected object (e.g. payload, event properties, session context, etc).',
            keywords=['start node'],
            icon='json',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={},
                outputs={
                    "payload": PortDoc(desc="This port returns defined data if injected into payload or empty object.")
                }
            )
        )
    )
