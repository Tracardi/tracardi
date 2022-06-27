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


class DeepCategorizationPlugin(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'DeepCategorizationPlugin':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return DeepCategorizationPlugin(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = MeaningCloudClient(credentials.get_credentials(self, Token).token)

    async def run(self, payload):
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
            manual="deep_categorization_action",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "text": None,
                "model": None
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="MeaningCloud resource",
                                description="Please select your MeaningCloud resource that contains your API token.",
                                component=FormComponent(type="resource", props={"label": "Resource"})
                            ),
                            FormField(
                                id="text",
                                name="Path to text",
                                description="Please type in the path to the text that you want to analyze.",
                                component=FormComponent(type="dotPath", props={"label": "Text"})
                            ),
                            FormField(
                                id="model",
                                name="Model",
                                description="Please type in the model to analyze your text with (for example "
                                            "IAB_2.0-tier4_en stands for IAB 2.0 Tier 4 model for english language).",
                                component=FormComponent(type="select", props={"label": "Model", "items": {
                                    "IAB_2.0": "IAB 2.0",
                                    "IAB_2.0-tier3": "IAB 2.0 Tier3",
                                    "IAB_2.0-tier4_en": "IAB 2.0 Tier 4",
                                    "Emotion": 'Emotion',
                                    "IntentionAnalysis": "Intention analysis",
                                    "VoC-Generic": "VoC Generic",
                                    "VoC-Banking": "VoC Banking",
                                    "VoC-Insurance": "VoC Insurance",
                                    "VoC-Retail": "VoC Retail",
                                    "VoC-Telco": "VoC Telco",
                                    "VoE-Performance": "VoE Performance",
                                    "VoE-Organization": "VoE Organization",
                                    "VoE-ExitInterview": "VoE ExitInterview"
                                }})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Categorize text',
            brand='Meaning cloud',
            desc='Categorizes text using MeaningCloud\'s deep categorization API.',
            icon='ai',
            group=["Machine learning"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns a response from MeaningCloud."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
