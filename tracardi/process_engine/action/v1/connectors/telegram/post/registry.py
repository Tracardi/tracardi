from tracardi.process_engine.action.v1.connectors.telegram.post.plugin import TelegramPostAction
from tracardi.service.plugin.domain.register import Plugin, Spec, Form, FormGroup, FormField, FormComponent, MetaData, \
    Documentation, PortDoc


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.telegram.post.plugin',
            className=TelegramPostAction.__name__,
            inputs=['payload'],
            outputs=['response', 'error'],
            version="0.8.0",
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "resource": {
                    "id": "",
                    "name": ""
                },
                "message": ""
            },
            manual="telegram/telegram_post_plugin",
            form=Form(
                groups=[
                    FormGroup(
                        name="Telegram post configuration",
                        fields=[
                            FormField(
                                id="resource",
                                name="Resource",
                                description="Select Telegram resource.",
                                component=FormComponent(type="resource", props={"label": "Telegram Resource", "tag": "telegram"})
                            ),
                            FormField(
                                id="message",
                                name="Message template",
                                description="Type the message. This is a message template you can use data placeholders.",
                                component=FormComponent(type="textarea", props={
                                    "label": "Message template"
                                })
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name="Telegram message",
            desc="Sends Telegram message via the bot.",
            brand="Telegram",
            icon="telegram",
            group=["Telegram"],
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
