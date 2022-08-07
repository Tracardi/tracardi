from tracardi.exceptions.exception import TracardiException
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, Token
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials
from tracardi.process_engine.action.v1.connectors.meaningcloud.client import MeaningCloudClient


def validate(config: dict) -> Config:
    return Config(**config)


class SummarizationPlugin(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SummarizationPlugin':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return SummarizationPlugin(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = MeaningCloudClient(credentials.get_credentials(self, Token).token)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        text = dot[self.config.text]
        lang = dot[self.config.lang]

        try:
            result = await self.client.summarize(text, lang, int(self.config.sentences))
            return Result(port="response", value=result)

        except TracardiException as e:
            return Result(port="error", value={"error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SummarizationPlugin',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            manual="summarization_action"
        ),
        metadata=MetaData(
            name='Summarize text',
            brand='Meaning cloud',
            desc='Summarizes given text using MeaningCloud\'s summarization API.',
            icon='ai',
            group=["Machine learning"],
            tags=['ai', 'ml'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns a response from MeaningCloud."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            ),
            pro=True
        )
    )
