from typing import List

from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    traits: List[str]


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class MaskTraitsAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload)

        for trait in self.config.traits:

            if dot.source(trait) == 'flow':
                self.console.warning("Flow values can not be hashed.")
                continue

            if dot.source(trait) == 'event':
                self.console.warning("Event values can not be modified in workflow.")
                continue

            elif not dot.validate(trait) or trait not in dot:
                self.console.warning(f"Given trait {trait} is invalid or does not exist.")
                continue

            dot[trait] = "###"

        if dot.profile:
            profile = Profile(**dot.profile)
            self.profile.replace(profile)

        if dot.session:
            session = Session(**dot.session)
            self.session.replace(session)

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
            license="MIT + CC",
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
            name='Mask data',
            desc='Mask defined data, e.g. profile traits.',
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
