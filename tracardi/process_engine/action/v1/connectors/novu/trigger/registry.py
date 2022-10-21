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
            version="0.7.2",
            license="MIT",
            author="Mateusz Zitaruk, Risto Kowaczewski",
            init={
                "source": {"id": "", "name": ""},
                "template": {"id": "", "name": ""},
                "subscriber_id": "profile@id",
                "recipient_email": "profile@pii.email",
                "payload": "{}"
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
                                id="template",
                                name="Novu template name",
                                description="Type the template name defined in Novu. This template will be used to send"
                                            " a message.",
                                component=FormComponent(type="autocomplete", props={
                                    "label": "Template name",
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
                                            "profile@pii.email.",
                                component=FormComponent(type="dotPath", props={"label": "E-mail address"})
                            ),
                            FormField(
                                id="payload",
                                name="Data",
                                description="Please type the data you would like to use within template. "
                                            "You may use the reference to data e.g. profile@pii.name. Please look for "
                                            "the term \"Object template\" in documentation for more details.",
                                component=FormComponent(type="json", props={"label": "Data"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name="Novu notifications",
            desc="Create and send notification to chosen recipient.",
            brand="Novu",
            icon="message",
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
