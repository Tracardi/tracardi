from tracardi.domain.profile import Profile

from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result

from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class InjectProfileByField(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        value = dot[self.config.value]

        result = await storage.driver.profile.load_by_field(self.config.field, value, start=0, limit=2)

        if result.total != 1:
            message = "Found {} records for {} = {}.".format(result.total, self.config.field, value)
            self.console.warning(message)
            return Result(port="error", value={"message": message})

        profile = Profile(**result.first())

        self.event.profile = profile
        self.event.metadata.profile_less = False
        self.event.update = True
        self.execution_graph.set_profiles(profile)

        return Result(port="profile", value=profile)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='InjectProfileByField',
            inputs=['payload'],
            outputs=['profile', 'error'],
            version='0.7.2',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "field": "pii.email",
                "value": "event@properties.email"
            },
            manual='profile_inject_action',
            form=Form(groups=[
                FormGroup(
                    name="Select profile",
                    fields=[
                        FormField(
                            id="field",
                            name="Profile field",
                            description="Select the PII profile field by which will be used to identify the profile.",
                            component=FormComponent(type="select", props={"label": "Field", "items": {
                                "pii.email": "E-mail",
                                "pii.telephone": "Phone",
                                "pii.twitter": "Twitter handle"
                            }})
                        ),
                        FormField(
                            id="value",
                            name="Value",
                            description="Type or reference the field value that you would like to use to find "
                                        "the profile.",
                            component=FormComponent(type="dotPath", props={"label": "Value"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Load profile by ...',
            desc='Loads and replaces current profile in the workflow. It also assigns loaded profile to current event. '
                 'It basically replaces the current profile with loaded one.',
            icon='profile',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "profile": PortDoc(desc="Returns loaded profile."),
                    "error": PortDoc(desc="Returns error.")
                }
            )
        )
    )
