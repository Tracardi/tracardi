from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from ..add_contact.model.config import Connection
from tracardi.service.domain import resource as resource_db
from ..client import ElasticEmailClient


def validate(config: dict) -> Config:
    return Config(**config)


class ElasticEmailContactStatusChange(ActionRunner):

    config: Config
    credentials: Connection
    client: ElasticEmailClient

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config    # type: Config
        self.credentials = resource.credentials.get_credentials(self, output=Connection)    # type: Connection
        self.client = ElasticEmailClient(**dict(self.credentials))    # type: ElasticEmailClient

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        contact_data = {
            "email": dot[self.config.email],
            'status': dot[self.config.status],
        }

        try:
            result = await self.client.contact_status_change(
                contact_data
            )
            return Result(port="response", value=result)
        except Exception as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ElasticEmailContactStatusChange',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT + CC",
            author="Ben Ullrich",
            manual="elastic_email_change_contact_status_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "email": None,
                "status": None,
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Elastic Email resource",
                                description="Please select your Elastic Email resource, containing your api key",
                                component=FormComponent(type="resource",
                                    props={"label": "Resource", "tag": "elasticemail"})
                            ),
                            FormField(
                                id="email",
                                name="Email address",
                                description="Please type in the path to the email address for your new contact.",
                                component=FormComponent(type="dotPath", props={"label": "Email",
                                                                               "defaultSourceValue": "profile",
                                                                               "defaultPathValue": "data.contact.email.main"
                                                                               })
                            ),
                            FormField(
                                id="status",
                                name="Status",
                                description="The path to the status as a number or just the number for the new status. "
                                            "2 is unsubscribe",
                                component=FormComponent(type="dotPath", props={"label": "Status",
                                                                               "defaultSourceValue": "profile",
                                                                               "defaultPathValue": "aux.status"
                                                                               })
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Change Contact Status',
            brand='Elastic Email',
            desc='Changes the status of a contact on Elastic Email based on provided data.',
            icon='email',
            group=["Elastic Email"],
            tags=['mailing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from Elastic Email API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
