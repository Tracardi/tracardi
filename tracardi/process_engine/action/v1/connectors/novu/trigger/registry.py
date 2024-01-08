from tracardi.process_engine.action.v1.connectors.novu.trigger.plugin import Endpoint
from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.novu.trigger.plugin',
            className='NovuTriggerAction',
            inputs=['payload'],
            outputs=['response', 'error'],
            version="0.8.2",
            license="MIT + CC",
            author="Mateusz Zitaruk, Risto Kowaczewski",
            init={
                "source": {"id": "", "name": ""},
                "template": {"id": "", "name": ""},
                "subscriber_id": "profile@id",
                "recipient_email": "profile@data.contact.email.main",
                "payload": "{}",
                "hash": False,
                "upsert_subscriber": True,
                "tenant": {"id": "", "name": ""},
            },
            manual="novu_plugin_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Novu notification configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Resource",
                                description="Select your api key resource containing your key from novu",
                                component=FormComponent(type="resource", props={"label": "resource", "tag": "novu"})
                            ),
                            FormField(
                                id="tenant",
                                name="Novu tenant",
                                description="Select Novu tenant.",
                                component=FormComponent(type="autocomplete", props={
                                    "label": "Tenant",
                                    "endpoint": {
                                        "url": Endpoint.url(
                                            'tracardi.process_engine.action.v1.connectors.novu.trigger.plugin',
                                            'get_tenants'),
                                        "method": "post"
                                    },
                                })
                            ),
                            FormField(
                                id="template",
                                name="Novu message workflow",
                                description="Select the workflow defined in Novu. This workflow will be used to send"
                                            " a message.",
                                component=FormComponent(type="autocomplete", props={
                                    "label": "Workflow name",
                                    "endpoint": {
                                        "url": Endpoint.url(
                                            'tracardi.process_engine.action.v1.connectors.novu.trigger.plugin',
                                            'get_templates'),
                                        "method": "post"
                                    },
                                })
                            ),
                            FormField(
                                id="subscriber_id",
                                name="Subscriber ID",
                                description="Type path to subscriber ID. By default we use profile id.",
                                component=FormComponent(type="dotPath", props={"label": "Subscriber ID"})
                            ),
                            FormField(
                                id="upsert_subscriber",
                                name="Add Profile to Novu if not exists",
                                description="Select if profile should be added as subscriber if it does not exist. "
                                            "Subscriber ID will be used to identify profile.",
                                component=FormComponent(type="bool", props={"label": "Add profile to novu"})
                            ),
                            FormField(
                                id="hash",
                                name="Hash Subscriber ID",
                                description="Select if the defined subscriber id should be hashed. This can be useful "
                                            "if ID is made out of e.g e-mail.",
                                component=FormComponent(type="bool", props={"label": "Hash Subscriber ID"})
                            )
                        ]
                    ),
                    FormGroup(
                        name="E-mail configuration",
                        fields=[
                            FormField(
                                id="recipient_email",
                                name="Recipient e-mail address",
                                description="Please type a reference path to e-mail address. By default we set it to "
                                            "profile@data.contact.email.main",
                                component=FormComponent(type="dotPath", props={"label": "E-mail address"})
                            ),
                            FormField(
                                id="payload",
                                name="Data",
                                description="Please type the data you would like to use within template. "
                                            "You may use the reference to data e.g. profile@data.pii.firstname. Please look for "
                                            "the term \"Object template\" in documentation for more details.",
                                component=FormComponent(type="json", props={"label": "Data"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name="Trigger message",
            desc="Creates and sends notification to chosen recipient.",
            brand="Novu",
            icon="entity",
            tags=['email','chat', 'sms'],
            group=["Novu"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response status and content."),
                    "error": PortDoc(desc="This port returns error if request will fail ")}
            )
        )
    )
