import aiohttp
from tracardi.domain.resources.token import Token

from tracardi.domain.resource import ResourceCredentials
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration
from tracardi.service.notation.dot_template import DotTemplate


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class SentimentAnalysisAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SentimentAnalysisAction':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return SentimentAnalysisAction(config, resource.credentials)

    def __init__(self, config: Configuration, credentials: ResourceCredentials):
        self.credentials = credentials.get_credentials(self, output=Token)
        self.config = config

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()
        async with aiohttp.ClientSession() as session:
            params = {
                "key": self.credentials.token,
                "lang": self.config.language,
                "txt": template.render(self.config.text, dot)
            }
            try:
                async with session.post('https://api.meaningcloud.com/sentiment-2.1', params=params) as response:
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
            license="MIT",
            author="Risto Kowaczewski",
            manual="sentiment_analysis_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "language": "en",
                "text": None
            },
            form=Form(groups=[
                FormGroup(
                    name="Text sentiment resource",
                    fields=[
                        FormField(
                            id="source",
                            name="MeaningCloud resource",
                            description="Select MeaningCloud resource. Authentication credentials will be used to "
                                        "connect to MeaningCloud server.",
                            component=FormComponent(
                                type="resource",
                                props={"label": "resource", "tag": "token"})
                        )
                    ]
                ),
                FormGroup(
                    name="Text sentiment settings",
                    fields=[
                        FormField(
                            id="language",
                            name="Language",
                            description="Select language.",
                            component=FormComponent(type="select", props={
                                "label": "Language",
                                "items": {
                                    "en": "English",
                                    "sp": "Spanish",
                                    "fr": "French",
                                    "it": "Italian",
                                    "pt": "Portuguese",
                                    "ct": "Catalan"
                                }
                            })
                        ),
                        FormField(
                            id="text",
                            name="Text",
                            description="Type text to classify.",
                            component=FormComponent(type="textarea", props={"rows": 8})
                        )
                    ])
            ]),
        ),
        metadata=MetaData(
            name='Sentiment analysis',
            desc='It connects to the service that predicts sentiment from a given sentence.',
            icon='paragraph',
            group=["Machine learning"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="Returns result."),
                    "error": PortDoc(desc="Gets triggered if an error occurs.")
                }
            )
        )
    )
