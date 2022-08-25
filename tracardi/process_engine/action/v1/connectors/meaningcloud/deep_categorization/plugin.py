from tracardi.exceptions.exception import TracardiException
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, Token
from tracardi.service.storage.driver import storage
from tracardi.process_engine.action.v1.connectors.meaningcloud.client import MeaningCloudClient


def validate(config: dict) -> Config:
    return Config(**config)


class DeepCategorizationPlugin(ActionRunner):

    client: MeaningCloudClient
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.client = MeaningCloudClient(resource.credentials.get_credentials(self, Token).token)
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        text = dot[self.config.text]

        try:

            result = await self.client.deep_categorization(text, self.config.model)
            return Result(port="response", value=result)

        except TracardiException as e:
            return Result(port="error", value={"error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='DeepCategorizationPlugin',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            manual="deep_categorization_action"
        ),
        metadata=MetaData(
            name='Categorize text',
            brand='Meaning cloud',
            desc='Categorizes text using MeaningCloud\'s deep categorization API.',
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
