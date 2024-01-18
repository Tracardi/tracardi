from typing import List

from pydantic import field_validator
from tracardi.domain.profile import Profile

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig


class MergeProfileConfiguration(PluginConfig):
    mergeBy: List[str]

    @field_validator("mergeBy")
    @classmethod
    def list_must_not_be_empty(cls, value):
        # Merge by keys must exist and come from profile
        if not len(value) > 0:
            raise ValueError("Field mergeBy is empty and has no effect on merging. "
                             "Add merging key or remove this action from flow.")

        for key in value:
            if not key.startswith('profile@'):
                raise ValueError(
                    f"Field `{key}` does not start with profile@... Only profile fields are used during merging.")

        return value


def validate(config: dict) -> MergeProfileConfiguration:
    return MergeProfileConfiguration(**config)


class MergeProfilesAction(ActionRunner):
    merge_key: List[str]

    async def set_up(self, init):
        config = validate(init)
        self.merge_key = [key.lower() for key in config.mergeBy]

    async def run(self, payload: dict, in_edge=None) -> Result:
        if isinstance(self.profile, Profile):
            # TODO LOOK for self.profile.needs_merging()
            # TODO operation can be overwritten by update form cache. maybe mrege here not at the end of workflow.
            self.profile.set_merge_key(self.merge_key)
        else:
            if self.event.metadata.profile_less is True:
                self.console.warning("Can not merge profile when processing profile less events.")
            else:
                message = "Can not merge profile. Profile is empty."
                self.console.error(message)
                return Result(value={"message": message}, port="error")

        return Result(value=payload, port="payload")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MergeProfilesAction',
            inputs=["payload"],
            outputs=["payload", "error"],
            init={"mergeBy": []},
            version="0.8.2",
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="mergeBy",
                            name="Merge by fields",
                            description="Provide a list of fields that can identify user. For example profile@data.contact.email.main. "
                                        "These fields will be treated as primary keys for merging. Profiles will be "
                                        "grouped by this value and merged.",
                            component=FormComponent(type="listOfDotPaths", props={"label": "condition",
                                                                                  "defaultSourceValue": "profile"
                                                                                  })
                        )
                    ]
                ),
            ]),
            manual="merge_profiles_action"
        ),
        metadata=MetaData(
            name='Merge profiles',
            desc='Merges profile in storage when flow ends. This operation is expensive so use it with caution, '
                 'only when there is a new PII information added.',
            icon='merge',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns exactly same payload as given one.")
                }
            )
        )
    )
