from tracardi.process_engine.action.v1.connectors.matomo.client import MatomoClient, MatomoClientException
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .model.config import Config, MatomoPayload


def validate(config: dict) -> Config:
    return Config(**config)


class SendEventToMatomoAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SendEventToMatomoAction':
        config = Config(**kwargs)
        credentials = (await storage.driver.resource.load(config.source.id)).credentials
        return SendEventToMatomoAction(config, credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = MatomoClient(**credentials.get_credentials(self))

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        # TODO DIMENSIONS
        # TODO CONVERT TO ACTUAL DATA
        data = MatomoPayload(
            idsite=3,
            action_name="page-view",
            url="http://localhost:8686/tracker/",
            _id="26a721e2-77d6-4b59-9933-2562dcf20273".replace("-", "")[0:16],
            urlref=None,
            _idvc=2,
            _viewts=1649371076,
            _idts=1649341076,
            _rcn=None,
            _rck=None,
            res="1280x1024",
            ua="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 "
               "Safari/537.36",
            lang="pl-PL",
            uid="26a721e2-77d6-4b59-9933-2562dcf20273".replace("-", "")[0:16],
            new_visit=1,
            search="search-keyword",
            search_cat="search-category",
            search_count=13,
            pv_id="123abc",
            idgoal=1,
            revenue=10,
            gt_ms=60, # TODO TAKE LATER FROM EVENT

        )

        try:
            await self.client.send_event(data)
            return Result(port="response", value=payload)

        except MatomoClientException as e:
            return Result(port="error", value=str(e))


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SendEventToMatomoAction',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            #manual,
            init={
                "source": {
                    "id": None,
                    "name": None
                }
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Matomo resource",
                                description="Please select your Matomo resource, containing Matomo URL and token.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "matomo"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Send event to Matomo',
            desc='Sends currently processed event to Matomo.',
            icon='plugin',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns payload if everything is OK."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
