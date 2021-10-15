from typing import List

from pydantic import BaseModel, validator
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class MergeProfileConfiguration(BaseModel):
    mergeBy: List[str]

    @validator("mergeBy")
    def list_must_not_be_empty(cls, value):
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

    def __init__(self, **kwargs):
        config = validate(kwargs)
        self.merge_key = [key.lower() for key in config.mergeBy]

    async def run(self, payload):
        self.profile.operation.merge = self.merge_key
        return Result(value={}, port="payload")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.operations.merge_profiles_action',
            className='MergeProfilesAction',
            inputs=["payload"],
            outputs=["payload"],
            init={"mergeBy": []},
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="mergeBy",
                            name="Merge by fields",
                            description="Provide a list od fields that can identify user. These fields will be treated"
                                        " as primary keys for merging.",
                            component=FormComponent(type="listOfDotPaths", props={"label": "condition"})
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
            type='flowNode',
            width=200,
            height=100,
            icon='merge',
            group=["Operations"]
        )
    )
