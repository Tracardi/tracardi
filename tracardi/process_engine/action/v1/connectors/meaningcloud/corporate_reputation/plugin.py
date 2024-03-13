from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, Token
from tracardi.service.domain import resource as resource_db
from tracardi.process_engine.action.v1.connectors.meaningcloud.client import MeaningCloudClient


def validate(config: dict) -> Config:
    return Config(**config)


class CorporateReputationPlugin(ActionRunner):

    client: MeaningCloudClient
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.client = MeaningCloudClient(resource.credentials.get_credentials(self, Token).token)
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        text = dot[self.config.text]
        lang = dot[self.config.lang]

        try:
            result = await self.client.corporate_reputation(
                text,
                lang,
                self.config.relaxed_typography,
                self.config.focus,
                self.config.company_type
            )
            return Result(port="response", value=result)

        except Exception as e:
            return Result(port="error", value={"error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='CorporateReputationPlugin',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="corporate_reputation_action"
        ),
        metadata=MetaData(
            name='Corporate reputation',
            brand='Meaning cloud',
            desc='Corporates reputation using given text with MeaningCloud\'s corporate reputation 2.0 API.',
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
