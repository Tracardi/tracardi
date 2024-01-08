from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.sms77.sendsms.plugin',
            className='Sms77SendSmsAction',
            inputs=['payload'],
            outputs=['response', 'error'],
            version="0.7.2",
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "resource": {
                    "id": "",
                    "name": ""
                },
                "message": "",
                "recipient": "profile@pii.telephone",
                "sender": ""
            },
            manual="sms77/sms77_send_sms_plugin",
            form=Form(
                groups=[
                    FormGroup(
                        name="SMS77 notification configuration",
                        fields=[
                            FormField(
                                id="resource",
                                name="Resource",
                                description="Select your SMS77 resource.",
                                component=FormComponent(type="resource", props={"label": "SMS77 Resource", "tag": "sms77"})
                            ),
                            FormField(
                                id="message",
                                name="Message template",
                                description="Type the SMS message. This is a message template you can use data placeholders.",
                                component=FormComponent(type="textarea", props={
                                    "label": "Message template"
                                })
                            ),
                            FormField(
                                id="sender",
                                name="Sender",
                                description="Type sender or leave it blank if you would like to use default sender. "
                                            "Custom sender name can be found in Sms77 system.",
                                component=FormComponent(type="dotPath", props={"label": "Sender"})
                            ),
                            FormField(
                                id="recipient",
                                name="Recipient",
                                description="Type or reference SMS recipient phone number.",
                                component=FormComponent(type="dotPath", props={"label": "Recipient"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name="Send SMS",
            desc="Send SMS via Sms77 gateway.",
            brand="Sms77",
            icon="sms",
            group=["Sms77"],
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
