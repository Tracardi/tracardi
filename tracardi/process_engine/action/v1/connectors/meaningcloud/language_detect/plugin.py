import asyncio

from aiohttp import ClientConnectorError
from tracardi.domain.resources.token import Token
from tracardi_dot_notation.dot_template import DotTemplate
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from .model.configuration import Configuration
from tracardi.service.storage.driver import storage
from .service.http_client import HttpClient
from tracardi_plugin_sdk.domain.result import Result
from tracardi.domain.resource import ResourceCredentials


def validate(config: dict):
    return Configuration(**config)


class LanguageDetectAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'LanguageDetectAction':

        # This reads config
        config = validate(kwargs)

        # This reads resource
        resource = await storage.driver.resource.load(config.source.id)

        return LanguageDetectAction(config, resource.credentials)

    def __init__(self, config: Configuration, credentials: ResourceCredentials):
        self.message = config.message
        self.client = HttpClient(credentials.get_credentials(self, Token).token, config.timeout)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()
        string = template.render(self.message, dot)
        try:

            status, result = await self.client.send(string)
            return Result(port="response", value=result)

        except ClientConnectorError as e:
            return Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="error", value="Timeout.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='LanguageDetectAction',
            inputs=["payload"],
            outputs=['response', 'error'],
            version='0.6.1',
            license="MIT",
            author="Patryk Migaj, Risto Kowaczewski",
            manual="lang_detection_action",
            init={
                'source': {
                    'id': None,
                    'name': None
                },
                "message": "Hello world",
                "timeout": 15,
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="source",
                            name="Token resource",
                            description="Select resource that have API token.",
                            component=FormComponent(type="resource", props={"label": "resource"})
                        ),
                        FormField(
                            id="timeout",
                            name="Service time-out",
                            description="Type when to time out if service unavailable.",
                            component=FormComponent(type="text", props={"label": "time-out"})
                        )
                    ]
                ),
                FormGroup(
                    fields=[
                        FormField(
                            id="message",
                            name="Text",
                            description="Type text or path to text to be detected.",
                            component=FormComponent(type="textarea", props={"label": "template"})
                        )
                    ]
                )
            ]
            )
        ),
        metadata=MetaData(
            name='Language detection',
            desc='This plugin detect language from given string with meaningcloud API',
            icon='language',
            group=["Language"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "response": PortDoc(desc="Returns language detection service response."),
                    "error": PortDoc(desc="Returns error message."),
                }
            )
        )
    )
