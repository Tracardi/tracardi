from tracardi.domain.entity import Entity
from tracardi.process_engine.action.v1.internal.assign_profile_id.model.config import Configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class AssignProfileIdAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):

        dot = self._get_dot_accessor(payload)
        value = dot[self.config.value]

        if not isinstance(value, str):
            raise ValueError("Profile id must be a string.")

        if self.debug is True:
            self.console.warning("Your requested a change in event profile but events may not be updated in debug mode.")
        else:
            if self.event.profile is None:
                self.event.profile = Entity(id=value)
                self.event.metadata.profile_less = False
            else:
                self.event.profile.id = value
            self.event.update = True

        return Result(port='payload', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AssignProfileIdAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={"value": ""},
            manual="assign_profile_id_action",
            form=Form(groups=[
                FormGroup(
                    name="Value to hash",
                    fields=[
                        FormField(
                            id="value",
                            name="Profile id",
                            description="This value may be a reference to value.",
                            component=FormComponent(type="dotPath",
                                                    props={"label": "value"})
                        )
                    ]
                ),
            ]),

        ),
        metadata=MetaData(
            name='Assign profile id',
            desc='Assigns new profile id to the event.',
            icon='hash',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns input payload.")
                }
            )
        )
    )
