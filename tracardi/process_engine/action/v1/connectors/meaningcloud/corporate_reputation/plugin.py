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


class CorporateReputationPlugin(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'CorporateReputationPlugin':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return CorporateReputationPlugin(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = MeaningCloudClient(credentials.get_credentials(self, Token).token)

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
            license="MIT",
            author="Dawid Kruk",
            manual="corporate_reputation_action",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "text": None,
                "lang": "auto",
                "focus": None,
                "company_type": None,
                "relaxed_typography": False
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
                                id="lang",
                                name="Path to language",
                                description="Please type in the path to the language of given text. You can provide "
                                            "the language itself as well. Language should be in form of its "
                                            "MeaningCloud code (for example 'en' for English). You can also leave it on"
                                            " auto mode, so the language gets detected automatically.",
                                component=FormComponent(type="dotPath", props={"label": "Language"})
                            ),
                            FormField(
                                id="focus",
                                name="Focus on company",
                                description="You can type in the name of the company to focus on when analyzing text. "
                                            "This field is optional.",
                                component=FormComponent(type="text", props={"label": "Company name"})
                            ),
                            FormField(
                                id="company_type",
                                name="Filter by company type",
                                description="You can specify the type of company that you want to filter results by. "
                                            "Please provide it according to MeaningCloud's ontology types, so for "
                                            "example 'Top>Organization>Company>IndustrialCompany'. This field is "
                                            "optional as well.",
                                component=FormComponent(type="text", props={"label": "Company type"})
                            ),
                            FormField(
                                id="relaxed_typography",
                                name="Relaxed typography",
                                description="Please specify whether API should be strict in typography (spelling, "
                                            "mistakes), or not.",
                                component=FormComponent(type="bool", props={"label": "Enable relaxed typography"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Corporate reputation',
            brand='Meaning cloud',
            desc='Corporates reputation using given text with MeaningCloud\'s corporate reputation 2.0 API.',
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
