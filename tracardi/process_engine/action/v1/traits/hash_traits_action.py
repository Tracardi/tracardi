import hashlib
import json
from typing import List
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    traits: List[str]
    func: str = 'md5'


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class HashTraitsAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload)

        for trait in self.config.traits:

            if dot.source(trait) == 'flow':
                self.console.warning("Flow values can not be hashed.")
                continue
                
            elif not dot.validate(trait) or trait not in dot:
                self.console.warning(f"Given trait {trait} is invalid or does not exist.")
                continue

            value = dot[trait]

            if not isinstance(value, str):
                value = json.dumps(value)

            if self.config.func == 'md5':
                result = hashlib.md5(value.encode())
            elif self.config.func == 'sha256':
                result = hashlib.sha256(value.encode())
            elif self.config.func == 'sha1':
                result = hashlib.sha1(value.encode())
            elif self.config.func == 'sha512':
                result = hashlib.sha512(value.encode())
            else:
                result = hashlib.md5(value.encode())

            dot[trait] = result.hexdigest()

        if dot.profile:
            profile = Profile(**dot.profile)
            self.profile.replace(profile)

        if dot.session:
            session = Session(**dot.session)
            self.session.replace(session)

        event = Event(**dot.event)
        self.event.replace(event)

        return Result(port='payload', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='HashTraitsAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.7.0',
            license="MIT",
            author="Risto Kowaczewski",
            init={"traits": [], "func": "md5"},
            form=Form(groups=[
                FormGroup(
                    name="Traits to hash",
                    fields=[
                        FormField(
                            id="traits",
                            name="Reference value to be hashed",
                            description="If this value is not a string then it will be serialized to JSON and hashed.",
                            component=FormComponent(type="listOfDotPaths",
                                                    props={"label": "traits", "defaultSourceValue": "profile"})
                        ),
                        FormField(
                            id="func",
                            name="Hashing function",
                            description="Select hashing method.",
                            component=FormComponent(type="select",
                                                    props={"label": "Hashing", "items": {
                                                        "md5": "MD5",
                                                        "sha1": "SHA1",
                                                        "sha256": "SHA256",
                                                        "sha512": "SHA512"
                                                    }})
                        )
                    ]
                ),
            ]),

        ),
        metadata=MetaData(
            name='Hash data',
            desc='Hash defined data e.g. profile traits.',
            icon='hash',
            group=["Operations"],
            tags=['profile', 'trait', 'data'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload.")
                }
            )
        )
    )
