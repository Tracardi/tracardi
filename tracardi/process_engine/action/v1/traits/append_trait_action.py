from typing import Dict, List, Optional, Any, Union

from pydantic import validator, ValidationError, field_validator
from pydantic_core.core_schema import ValidationInfo

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner

from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    append: Optional[Dict[str, Any]] = {}
    remove: Optional[Dict[str, Union[Any, List[Any]]]] = {}

    @field_validator("remove")
    def validate_remove(cls, value, info: ValidationInfo):
        values = info.data
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
            print(destination, value, destination in dot)
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
            if not isinstance(dot.profile['traits'], dict):
                raise ValueError("Error when appending profile@traits to value `{}`. "
                                 "Private must have key:value pair. "
                                 "E.g. `name`: `{}`".format(dot.profile['traits'],
                                                            dot.profile['traits']))
            try:
                profile = Profile(**dot.profile)
            except ValidationError as e:
                self.console.error(f"Profile could not be updated. Some values where set incorrectly. "
                                   f"Please see the error {str(e)}")
                return Result(port="error", value=payload)

            self.profile.replace(profile)
        else:
            if dot.profile:
                self.console.warning("Profile changes were discarded in node `Append/Remove Trait`. "
                                     "This event is profile less so there is no profile.")

        if 'id' in dot.session:
            try:
                session = Session(**dot.session)
            except ValidationError as e:
                self.console.error(f"Session could not be updated. Some values where set incorrectly. "
                                   f"Please see the error {str(e)}")
                return Result(port="error", value=payload)

            self.session.replace(session)

        self.update_profile()

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=AppendTraitAction.__name__,
            inputs=['payload'],
            outputs=["payload", "error"],
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
            license="MIT + CC",
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
                                            " to configuration."),
                    "error": PortDoc(desc="This port returns error if appending was not successful.")
                }
            )
        )
    )
