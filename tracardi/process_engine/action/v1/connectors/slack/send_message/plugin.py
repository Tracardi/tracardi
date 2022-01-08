from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from .model.config import Config, Token
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.storage.driver import storage
from tracardi.process_engine.action.v1.connectors.slack.slack_client import SlackClient
from tracardi_dot_notation.dot_template import DotTemplate
from fastapi import HTTPException


def validate(config: dict) -> Config:
    return Config(**config)


class SlackPoster(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SlackPoster':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return SlackPoster(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self._client = SlackClient(credentials.get_credentials(self, Token).token)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        self.config.channel = dot[self.config.channel]

        template = DotTemplate()
        self.config.message = template.render(self.config.message, dot)

        try:
            response = await self._client.send_to_channel_as_bot(self.config.channel, self.config.message)
        except HTTPException:
            return Result(port="error", value={})

        return Result(port="response", value=response)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SlackPoster',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk",
            manual="send_to_slack_channel_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "channel": None,
                "message": None
            },
            form=Form(
                name="Plugin configuration",
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="source",
                                name="Slack resource",
                                description="Please select your Slack resource.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "token"})
                            ),
                            FormField(
                                id="channel",
                                name="Slack channel",
                                description="Please provide the name of the channel that you want the plugin to post "
                                            "to.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="message",
                                name="Message",
                                description="Please type in your message. You are free to use dot template.",
                                component=FormComponent(type="textarea", props={"label": "Message"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Post to Slack channel',
            desc='Posts defined message to a Slack channel.',
            icon='plugin',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns a response from Slack API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
