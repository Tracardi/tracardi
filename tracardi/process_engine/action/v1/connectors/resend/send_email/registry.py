from tracardi.process_engine.action.v1.connectors.resend.send_email.plugin import ResendSendEmailAction
from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.resend.send_email.plugin',
            className=ResendSendEmailAction.__name__,
            inputs=['payload'],
            outputs=['response', 'error'],
            version="0.8.2",
            license="MIT",
            author="RyomaHan(ryomahan1996@gmail.com)",
            init={
                "resource": {
                    "id": "",
                    "name": ""
                },
                "params": {},
            },
            form=Form(
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="resource",
                                name="Resend Resource",
                                required=True,
                                description="Select Resend Resource.",
                                component=FormComponent(type="resource", props={"label": "Resend Resource", "tag": "resend"})
                            ),
                        ]
                    ),
                    FormGroup(
                        name="Resend Send Email API Params",
                        fields=[
                            FormField(
                                id="params.sender",
                                name="Sender Email Address",
                                required=True,
                                description="To include a friendly name, use the format \"Your Name <sender@domain.com>\".",
                                component=FormComponent(type="dotPath", props={"label": "Resend"})
                            ),
                            FormField(
                                id="params.to",
                                name="Recipient Email Address(es)",
                                required=True,
                                description="Recipient email address. For multiple addresses, send as an array of strings, such as: [recipient@domain.com,...]. Max 50.",
                                component=FormComponent(type="dotPath", props={"label": "Resend"})
                            ),
                            FormField(
                                id="params.subject",
                                name="Email Subject",
                                required=True,
                                component=FormComponent(type="dotPath", props={"label": "Resend"})
                            ),
                            FormField(
                                id="params.bcc",
                                name="Bcc Recipient Email Address",
                                description="Bcc recipient email address. For multiple addresses, send as an array of strings, such as: [bcc@domain.com,...].",
                                component=FormComponent(type="dotPath", props={"label": "Resend"})
                            ),
                            FormField(
                                id="params.cc",
                                name="Cc Recipient Email Address",
                                description="Cc recipient email address. For multiple addresses, send as an array of strings, such as: [cc@domain.com,...].",
                                component=FormComponent(type="dotPath", props={"label": "Resend"})
                            ),
                            FormField(
                                id="params.reply_to",
                                name="Reply-to Email Address",
                                description="Reply-to email address. For multiple addresses, send as an array of strings, such as: [reply_to@domain.com,...].",
                                component=FormComponent(type="dotPath", props={"label": "Resend"})
                            ),
                            FormField(
                                id="params.message",
                                name="Message",
                                description="The HTML version of the message or the plain text version of the message.",
                                component=FormComponent(
                                    type="contentInput",
                                    props={
                                        "rows": 13,
                                        "label": "Message body",
                                        "allowedTypes": ["text/plain", "text/html"]
                                    })
                            ),
                            FormField(
                                id="params.headers",
                                name="Custom Headers",
                                description="Custom headers to add to the email.",
                                component=FormComponent(type="dotPath", props={"label": "Resend"})
                            ),
                        ]
                    ),
                ]
            )
        ),
        metadata=MetaData(
            name="Resend: Send Email",
            desc="Send email(s) by Resend.",
            brand="Resend",
            icon="resend",
            group=["Resend"],
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
