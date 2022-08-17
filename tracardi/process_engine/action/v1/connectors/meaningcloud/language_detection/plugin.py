import asyncio

from aiohttp import ClientConnectorError
from tracardi.domain.resources.token import Token
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration
from tracardi.service.storage.driver import storage
from .service.http_client import HttpClient
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
        self.client = HttpClient(
            credentials.get_credentials(self, Token).token,
            config.timeout,
            self.node.on_connection_error_repeat
        )

    async def run(self, payload: dict, in_edge=None) -> Result:
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
            version='0.6.2',
            license="MIT",
            author="Patryk Migaj, Risto Kowaczewski",
            manual="lang_detection_action",

        ),
        metadata=MetaData(
            name='Language detection',
            brand='Meaning cloud',
            desc='This plugin detect language from given string with meaningcloud API',
            icon='language',
            group=["Machine learning"],
            tags=['ai', 'ml'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "response": PortDoc(desc="Returns language detection service response."),
                    "error": PortDoc(desc="Returns error message."),
                }
            ),
            pro=True
        )
    )
