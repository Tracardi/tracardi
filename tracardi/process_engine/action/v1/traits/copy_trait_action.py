import logging

from pydantic import BaseModel

from tracardi.config import tracardi
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from deepdiff import DeepDiff
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session

from tracardi.process_engine.tql.utils.dictonary import flatten

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)


class TraitsConfiguration(BaseModel):
    set: dict = {}


class Configuration(BaseModel):
    traits: TraitsConfiguration


def validate(config: dict):
    return Configuration(**config)


class CopyTraitAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)
        self.mapping = self.config.traits.set

    async def run(self, payload: dict):

        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        for destination, value in self.mapping.items():
            dot[destination] = value

        logger.debug("NEW PROFILE: {}".format(dot.profile))



        if self.event.metadata.profile_less is False:
            if 'traits' not in dot.profile:
                raise ValueError("Missing traits in profile.")

            if 'private' not in dot.profile['traits']:
                raise ValueError("Missing `traits.private` in profile.")

            if 'public' not in dot.profile['traits']:
                raise ValueError("Missing `traits.public` in profile.")

            if not isinstance(dot.profile['traits']['private'], dict):
                raise ValueError(
                    "Error when setting profile@traits.private to value `{}`. Private must have key:value pair. "
                    "E.g. `name`: `{}`".format(dot.profile['traits']['private'], dot.profile['traits']['private']))

            if not isinstance(dot.profile['traits']['public'], dict):
                raise ValueError("Error when setting profile@traits.public to value `{}`. Public must have key:value pair. "
                                 "E.g. `name`: `{}`".format(dot.profile['traits']['public'],
                                                            dot.profile['traits']['public']))

            profile = Profile(**dot.profile)

            flat_profile = flatten(profile.dict())
            flat_dot_profile = flatten(Profile(**dot.profile).dict())
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

        session = Session(**dot.session)
        self.session.replace(session)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.copy_trait_action',
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
                    name="Copy/Set profile traits",
                    description="Define what data from event is to be copied to profile. You can also copy data the "
                                "other way around.",
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
            version='0.6.0',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Set Trait',
            desc='Returns payload with copied/set traits.',
            icon='copy',
            group=["Data processing"],
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
