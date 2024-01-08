from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.clicksend.sendsms.plugin',
            className='ClicksendSendSmsAction',
            inputs=['payload'],
            outputs=['response', 'error'],
            version="0.8.2",
            license="MIT",
            author="kokobhara",
            init={
                "resource": {
                    "id": "",
                    "name": ""
                },
                "message": "",
                "recipient": "profile@data.pii.telephone",
                "sender": ""
            },
            manual="clicksend_sms",
            form=Form(
                groups=[
                    FormGroup(
                        name="ClickSend notification configuration",
                        fields=[
                            FormField(
                                id="resource",
                                name="Resource",
                                description="Select your ClickSend resource.",
                                component=FormComponent(type="resource", props={"label": "ClickSend Resource", "tag": "clicksend"})
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
                                            "Custom sender name can be found in ClickSend system.",
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
            desc="Send SMS via ClickSend gateway.",
            brand="ClickSend",
            icon="chat",
            group=["SMS"],
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
