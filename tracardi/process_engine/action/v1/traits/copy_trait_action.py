import logging

from pydantic import BaseModel

from tracardi.config import tracardi
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from deepdiff import DeepDiff
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session

from tracardi.process_engine.tql.utils.dictonary import flatten
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.tracking.cache.profile_cache import save_profile_cache

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)


class TraitsConfiguration(BaseModel):
    set: dict = {}


class Configuration(PluginConfig):
    traits: TraitsConfiguration


def validate(config: dict):
    return Configuration(**config)


class CopyTraitAction(ActionRunner):

    mapping: dict
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)
        self.mapping = self.config.traits.set

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        for destination, value in self.mapping.items():
            dot[destination] = value

        logger.debug("NEW PROFILE: {}".format(dot.profile))

        if self.event.metadata.profile_less is False:
            if 'traits' not in dot.profile:
                raise ValueError("Missing traits in profile.")

            if not isinstance(dot.profile['traits'], dict):
                raise ValueError(
                    "Error when setting profile@traits to value `{}`. Traits must have key:value pair. "
                    "E.g. `name`: `{}`".format(dot.profile['traits'], dot.profile['traits']))

            profile = Profile(**dot.profile)

            flat_profile = flatten(profile.model_dump())
            flat_dot_profile = flatten(Profile(**dot.profile).model_dump())
            diff_result = DeepDiff(flat_dot_profile, flat_profile, exclude_paths=["root['metadata.time.insert']"])

            if diff_result and 'dictionary_item_removed' in diff_result:
                errors = [item.replace("root[", "profile[") for item in diff_result['dictionary_item_removed']]
                error_msg = "Some values were not added to profile. Profile schema seems not to have path: {}. " \
                            "This node is probably misconfigured.".format(errors)
                raise ValueError(error_msg)

            self.profile.replace(profile)
        else:
            if dot.profile:
                self.console.warning("Profile changes were discarded in node `Set Trait`. This event is profile "
                                     "less so there is no profile.")

        event = Event(**dot.event)
        self.event.replace(event)

        if 'id' in dot.session:
            session = Session(**dot.session)
            self.session.replace(session)

        self.update_profile()
        save_profile_cache(self.profile)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='CopyTraitAction',
            inputs=['payload'],
            outputs=["payload"],
            init={
                "traits": {
                    "set": {
                    }
                }
            },
            form=Form(groups=[
                FormGroup(
                    name="Copy data",
                    fields=[
                        FormField(
                            id="traits",
                            name="Define the copy/set actions",
                            description="Provide source and target data along with action you would like to perform.",
                            component=FormComponent(type="copyTraitsInput",
                                                    props={"actions": {"set": "Set to"},
                                                           "defaultAction": "set",
                                                           "defaultSource": "event@properties",
                                                           "defaultTarget": "profile@traits"
                                                           })
                        )
                    ]
                ),
            ]),
            version='0.8.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Copy data',
            desc='Copy event property to profile trait. This plugin copies event properties to defined destination.',
            icon='copy',
            tags=['profile', 'event', 'traits', 'memory', 'reference', 'data', "read", 'copy', 'properties'],
            group=["Data processing"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload modified according to configuration.")
                }
            )
        )
    )
