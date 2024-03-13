from typing import List
from pydantic import field_validator
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.plugin.domain.config import PluginConfig


class DeleteTraitConfiguration(PluginConfig):
    delete: List[str]

    @field_validator("delete")
    @classmethod
    def list_must_not_be_empty(cls, value):
        if not len(value) > 0:
            raise ValueError("List to delete must not be empty.")
        return value


def validate(config: dict):
    return DeleteTraitConfiguration(**config)


class DeleteTraitAction(ActionRunner):

    config: DeleteTraitConfiguration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        for value in self.config.delete:
            if value.startswith("event@"):
                self.console.warning(f"Could not delete value {value}, it is an event property and events "
                                     f"can not be changed in workflow.")
            try:
                del dot[value]
            except KeyError as e:
                self.console.warning(f"Could not delete value {value}, it is missing, details: {repr(e)}")

        if self.event.metadata.profile_less is False:
            profile = Profile(**dot.profile)
            self.profile.replace(profile)

        if 'id' in dot.session:
            session = Session(**dot.session)
            self.session.replace(session)

        self.update_profile()

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
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='delete_data'
        ),
        metadata=MetaData(
            name='Delete data',
            desc='Deletes data from internal state of the workflow.',
            icon='remove',
            group=["Data processing"],
            tags=['traits', 'profile', 'data'],
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
