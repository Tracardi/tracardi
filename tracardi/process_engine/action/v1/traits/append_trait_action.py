from typing import Dict, List, Optional, Any, Union

from pydantic import validator

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    append: Optional[Dict[str, Any]] = {}
    remove: Optional[Dict[str, Union[Any, List[Any]]]] = {}

    @validator("remove")
    def validate_remove(cls, value, values):
        if 'append' not in values and 'remove' not in values:
            raise ValueError("Please define `append` or `remove` in config section.")

        return value


def validate(config: dict):
    return Configuration(**config)


class AppendTraitAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        for destination, value in self.config.append.items():
            value = dot[value]
            if destination in dot:
                if not isinstance(dot[destination], list):
                    # Make it a list with original value
                    dot[destination] = [dot[destination]]

                if isinstance(value, list):
                    for v in value:
                        if v not in dot[destination]:
                            dot[destination].append(v)

                elif value not in dot[destination]:
                    dot[destination].append(value)
            else:
                dot[destination] = value

        for destination, value in self.config.remove.items():
            value = dot[value]
            if destination in dot:
                if not isinstance(dot[destination], list):
                    raise ValueError("Can not remove from non-list data.")

                if isinstance(value, list):
                    for v in value:
                        if v in dot[destination]:
                            dot[destination].remove(v)
                elif value in dot[destination]:
                    dot[destination].remove(value)

        if self.event.metadata.profile_less is False:
            if not isinstance(dot.profile['traits']['private'], dict):
                raise ValueError("Error when appending profile@traits.private to value `{}`. "
                                 "Private must have key:value pair. "
                                 "E.g. `name`: `{}`".format(dot.profile['traits']['private'],
                                                            dot.profile['traits']['private']))

            if not isinstance(dot.profile['traits']['public'], dict):
                raise ValueError(
                    "Error when appending profile@traits.public to value `{}`. Public must have key:value pair. "
                    "E.g. `name`: `{}`".format(dot.profile['traits']['public'], dot.profile['traits']['public']))

            profile = Profile(**dot.profile)
            self.profile.replace(profile)
        else:
            if dot.profile:
                self.console.warning("Profile changes were discarded in node `Append/Remove Trait`. "
                                     "This event is profile less so there is no profile.")

        event = Event(**dot.event)
        self.event.replace(event)

        if 'id' in dot.session:
            session = Session(**dot.session)
            self.session.replace(session)

        self.update_profile()

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.append_trait_action',
            className='AppendTraitAction',
            inputs=['payload'],
            outputs=["payload"],
            init={
                "append": {
                    "target1": "source1",
                    "target2": "source2",
                },
                "remove": {
                    "target": ["item1", "item2"]
                }
            },
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski",
            manual="append_remove_trait_action"
        ),
        metadata=MetaData(
            name='Append/Remove data',
            desc='Appends/Removes trait to/from given destination',
            icon='append',
            group=["Data processing"],
            tags=['traits', 'profile', 'reference', 'data'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload with traits appended or removed according"
                                            " to configuration.")
                }
            )
        )
    )
