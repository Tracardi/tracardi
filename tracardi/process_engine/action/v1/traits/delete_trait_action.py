from typing import List
from pydantic import BaseModel, validator
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session


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
        print(self.event, kwargs)
        self.config = validate(kwargs)

    async def run(self, payload: dict):
        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        for value in self.config.delete:
            try:
                del dot[value]
            except KeyError as e:
                self.console.warning("Could not delete value {} due to error: {}".format(value, str(e)))

        if self.event.metadata.profile_less is False:
            profile = Profile(**dot.profile)
            self.profile.replace(profile)

        session = Session(**dot.session)
        self.session.replace(session)

        event = Event(**dot.event)
        self.event.replace(event)

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
            desc='Deletes traits from profile or payload. Accepts dotted notation as definition of a field to be '
                 'deleted. Returns payload.',
            icon='remove',
            group=["Data processing"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload with selected fields deleted.")
                }
            )
        )
    )
