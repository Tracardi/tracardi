from typing import List
from pydantic import BaseModel, validator
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi.domain.profile import Profile


class DeleteTraitConfiguration(BaseModel):
    delete: List[str]

    @validator("delete")
    def list_must_not_be_empty(cls, value):
        if not len(value) > 0:
            raise ValueError("List to delete must not be empty.")
        return value


def validate(config: dict):
    return DeleteTraitConfiguration(**config)


class DeleteTraitAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload: dict):
        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        for value in self.config.delete:
            del dot[value]

        profile = Profile(**dot.profile)

        self.profile.replace(profile)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.delete_trait_action',
            className='DeleteTraitAction',
            inputs=['payload'],
            outputs=["payload"],
            init={
                "delete": []
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="delete",
                            name="Delete fields",
                            description="Type a list of fields that must be deleted.",
                            component=FormComponent(type="listOfDotPaths", props={"label": "Path to field"})
                        )
                    ]
                ),
            ]),
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Delete Trait',
            desc='Deletes traits from profile or payload. Accepts dotted notation as definition of a filed to be '
                 'deleted. Returns payload.',
            type='flowNode',
            width=100,
            height=100,
            icon='remove',
            group=["Data processing"]
        )
    )
