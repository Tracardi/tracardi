import logging
from tracardi.config import tracardi
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.domain.profile import Profile

from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.tracking.cache.profile_cache import save_profile_cache

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)


class Configuration(PluginConfig):
    mapping: dict


def validate(config: dict):
    return Configuration(**config)


class ModifyProfileAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        if self.profile is not None:

            dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

            if 'traits' not in dot.profile:
                raise ValueError("Missing traits in profile.")

            if not isinstance(dot.profile['traits'], dict):
                raise ValueError(
                    "Error when setting profile@traits to value `{}`. Traits must have key:value pair. "
                    "E.g. `name`: `{}`".format(dot.profile['traits'], dot.profile['traits']))

            for destination, value in self.config.mapping.items():
                dot[f"profile@{destination}"] = dot[value]

            profile = Profile(**dot.profile.dict())

            self.profile.replace(profile)
            self.update_profile()
            save_profile_cache(self.profile)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=ModifyProfileAction.__name__,
            inputs=['payload'],
            outputs=["payload"],
            init={
                "mapping": {}
            },
            form=Form(groups=[
                FormGroup(
                    name="Modify profile",
                    fields=[
                        FormField(
                            id="ModifyProfileAction",
                            name="Define the modifications",
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
            version='0.8.2',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Modify profile',
            desc='Modifies profile properties. This plugin copies event properties to defined destination.',
            icon='copy',
            tags=['profile', 'copy', 'properties'],
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
