from tracardi.service.storage.elastic.interface.collector.load.profile import load_profile
from tracardi.domain.profile import Profile
from tracardi.service.storage.driver.elastic import profile as profile_db
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
        field = self.config.field

        if field == 'id':
            profile = await load_profile(profile_id=value)

            if not profile:
                return Result(port="error", value={"message": "Could not find profile."})

        else:
            result = await profile_db.load_active_profile_by_field(self.config.field, value, start=0, limit=2)

            if result.total != 1:
                message = "Found {} records for {} = {}.".format(result.total, self.config.field, value)
                self.console.warning(message)
                return Result(port="error", value={"message": message})

            record = result.first()

            if not record:
                return Result(port="error", value={"message": "Could not find profile."})

            profile = record.to_entity(Profile)

        self.event.profile = profile
        self.event.metadata.profile_less = False

        self.execution_graph.set_profiles(profile)

        return Result(port="profile", value=profile.model_dump(mode='json'))


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='InjectProfileByField',
            inputs=['payload'],
            outputs=['profile', 'error'],
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "field": "data.contact.email.main",
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
                                "id": "Id",
                                "data.contact.email.main": "Main E-mail",
                                "data.contact.email.business": "Business E-mail",
                                "data.contact.email.private": "Private E-mail",
                                "data.contact.phone.main": "Main Phone",
                                "data.contact.phone.mobile": "Mobile Phone",
                                "data.contact.phone.business": "Business Phone",
                                "data.contact.app.twitter": "Twitter handle"
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
