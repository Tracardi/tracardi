from pydantic import BaseModel

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from deepdiff import DeepDiff
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session

from tracardi.process_engine.tql.utils.dictonary import flatten
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.wf.domain.flow_graph import FlowGraph

logger = get_logger(__name__)


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

    def _set_changes(self, dot,  mapping):
        flow: FlowGraph = self.flow

        for destination, value in mapping.items():
            if destination.startswith('event'):
                self.console.warning(f"Can not copy data to event. Events are imputable and can not be changed. "
                                     f"Property {destination} skipped.")
                continue

            # Value is automatically converted to value if in dot format
            old_value = dot[destination] if destination in dot else None
            dot[destination] = value
            if self.profile and destination.startswith('profile@'):
                flow.record_change(
                    field=destination[8:],
                    value=value,
                    old_value=old_value
                )

        self.flow = flow

        return dot

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)
        mapping = self.config.traits.set

        dot = self._set_changes(dot, mapping)

        if self.event.metadata.profile_less is False:
            if 'traits' not in dot.profile:
                message = "Missing traits in profile."
                self.console.error(message)
                return Result(port="error", value={"message": message})

            if not isinstance(dot.profile['traits'], dict):
                message = ("Error when setting profile@traits to value `{}`. Traits must have key:value pair. "
                           "E.g. `name`: `{}`").format(dot.profile['traits'], dot.profile['traits'])
                self.console.error(message)
                return Result(port="error", value={"message": message})

            profile = Profile(**dot.profile)

            flat_profile = flatten(profile.model_dump(mode='json'))
            flat_dot_profile = flatten(Profile(**dot.profile).model_dump(mode='json'))
            diff_result = DeepDiff(flat_dot_profile, flat_profile, exclude_paths=["root['metadata.time.insert']"])

            if diff_result and 'dictionary_item_removed' in diff_result:
                errors = [item.replace("root[", "profile[") for item in diff_result['dictionary_item_removed']]
                error_msg = "Some values were not added to profile. Profile schema seems not to have path: {}. " \
                            "This node is probably misconfigured.".format(errors)
                raise ValueError(error_msg)

            self.update_profile()
            self.profile.replace(profile)

        else:
            if dot.profile:
                self.console.warning("Profile changes were discarded in node `Copy data`. This event is profile "
                                     "less so there is no profile.")

        if 'id' in dot.session:
            session = Session(**dot.session)
            self.session.replace(session)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='CopyTraitAction',
            inputs=['payload'],
            outputs=["payload", "error"],
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
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='copy_data'
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
