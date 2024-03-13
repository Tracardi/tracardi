from tracardi.domain.resources.token import Token

from tracardi.service.domain import resource as resource_db
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.tracardi_http_client import HttpClient


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class SentimentAnalysisAction(ActionRunner):

    config: Configuration
    credentials: Token

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.credentials = resource.credentials.get_credentials(self, output=Token)
        self.config = config

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()
        async with HttpClient(self.node.on_connection_error_repeat) as client:
            params = {
                "key": self.credentials.token,
                "lang": self.config.language,
                "txt": template.render(self.config.text, dot)
            }
            try:
                async with client.post('https://api.meaningcloud.com/sentiment-2.1', params=params) as response:
                    if response.status != 200:
                        raise ConnectionError("Could not connect to service https://api.meaningcloud.com. "
                                              f"It returned `{response.status}` status.")

                    data = await response.json()
                    if 'status' in data and 'msg' in data['status']:
                        if data['status']['msg'] != "OK":
                            raise ValueError(data['status']['msg'])

                    result = {
                        "sentiment": data['score_tag'],
                        "agreement": data['agreement'],
                        "subjectivity": data['subjectivity'],
                        "confidence": float(data['confidence'])
                    }

                    return Result(port="result", value=result)
            except Exception as e:
                self.console.error(repr(e))
                return Result(port="error", value=str(e))


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SentimentAnalysisAction',
            inputs=["payload"],
            outputs=['result', 'error'],
            version='0.6.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="sentiment_analysis_action"

        ),
        metadata=MetaData(
            name='Sentiment analysis',
            brand='Meaning cloud',
            desc='It connects to the service that predicts sentiment from a given sentence.',
            icon='paragraph',
            group=["Machine learning"],
            tags=['ai', 'ml'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns result."),
                    "error": PortDoc(desc="Gets triggered if an error occurs.")
                }
            ),
            pro=True
        )
    )
