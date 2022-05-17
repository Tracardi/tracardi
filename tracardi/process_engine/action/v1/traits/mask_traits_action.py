from typing import List

from pydantic import BaseModel

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Configuration(BaseModel):
    traits: List[str]


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class MaskTraitsAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):

        dot = self._get_dot_accessor(payload)

        for trait in self.config.traits:

            if dot.source(trait) == 'flow':
                self.console.warning("Flow values can not be hashed.")
                continue

            dot[trait] = "###"

        profile = Profile(**dot.profile)
        self.profile.replace(profile)
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
            className='MaskTraitsAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.7.0',
            license="MIT",
            author="Risto Kowaczewski",
            init={"traits": []},
            form=Form(groups=[
                FormGroup(
                    name="Traits to hash",
                    fields=[
                        FormField(
                            id="traits",
                            name="Reference value to be masked",
                            description="Values with be masked with ###.",
                            component=FormComponent(type="listOfDotPaths",
                                                    props={"label": "traits", "defaultSourceValue": "profile"})
                        )
                    ]
                ),
            ]),

        ),
        metadata=MetaData(
            name='Mask traits',
            desc='Mask defined profile traits.',
            icon='hash',
            group=["Operations"],
            tags=['profile', 'trait'],
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
