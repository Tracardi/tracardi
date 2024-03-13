from tracardi.domain.resources.token import Token
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.domain import resource as resource_db
from tracardi.process_engine.action.v1.connectors.slack.slack_client import SlackClient
from tracardi.service.notation.dot_template import DotTemplate


def validate(config: dict) -> Config:
    return Config(**config)


class SlackPoster(ActionRunner):

    _client: SlackClient
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self._client = SlackClient(resource.credentials.get_credentials(self, Token).token)
        self._client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        channel = dot[self.config.channel]

        template = DotTemplate()
        message = template.render(self.config.message, dot)

        try:
            response = await self._client.send_to_channel_as_bot(channel, message)
        except ConnectionError as e:
            self.console.error(str(e))
            return Result(port="error", value={"detail": str(e)})

        return Result(port="response", value=response)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SlackPoster',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.1',
            license="MIT + CC",
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
                groups=[
                    FormGroup(
                        name="Slack configuration",
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
                                description="Please provide the name of the channel you want the plugin to post "
                                            "to.",
                                component=FormComponent(type="dotPath", props={"label": "Channel"})
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
            name='Post to Slack Channel',
            desc='Posts defined message to a Slack channel.',
            icon='slack',
            group=["Messaging"],
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
