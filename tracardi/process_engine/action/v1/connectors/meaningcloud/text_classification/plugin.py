from typing import Dict

from tracardi.service.tracardi_http_client import HttpClient
from tracardi.domain.resources.token import Token
from tracardi.service.domain import resource as resource_db
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from .model.configuration import Configuration
from tracardi.service.notation.dot_template import DotTemplate


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class TextClassificationAction(ActionRunner):

    models: Dict[str, str]
    config: Configuration
    credentials: Token

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.credentials = resource.credentials.get_credentials(self, Token)  # type: Token
        self.config = config
        self.models = {
            'social': 'SocialMedia',
            'press': 'IPTC'
        }

    async def run(self, payload: dict, in_edge=None) -> Result:

        if self.config.model not in self.models:
            raise ValueError(f"Model `{self.config.model}` is incorrect. Available models are `{self.models}`")

        dot = self._get_dot_accessor(payload)
        template = DotTemplate()
        async with HttpClient(self.node.on_connection_error_repeat) as client:
            params = {
                "key": self.credentials.token,
                "txt": template.render(self.config.text, dot),
                "model": "{}_{}".format(self.models[self.config.model], self.config.language)
            }

            if self.config.has_title():
                params['title'] = dot[self.config.title]

            try:
                async with client.post('https://api.meaningcloud.com/class-2.0', params=params) as response:
                    if response.status != 200:
                        raise ConnectionError("Could not connect to service https://api.meaningcloud.com. "
                                              f"It returned `{response.status}` status.")

                    data = await response.json()
                    if 'status' in data and 'msg' in data['status']:
                        if data['status']['msg'] != "OK":
                            raise ValueError(data['status']['msg'])

                    result = {
                        "categories": data['category_list'],
                    }

                    return Result(port="payload", value=result)

            except Exception as e:
                self.console.error(repr(e))
                return Result(port="error", value=str(e))


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='TextClassificationAction',
            inputs=["payload"],
            outputs=['payload', 'error'],
            version='0.6.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="text_classification_action"
        ),
        metadata=MetaData(
            name='Text classification',
            brand='Meaning cloud',
            desc='It connects to the service that classifies a given sentence.',
            icon='ai',
            group=["Machine learning"],
            tags=['ai', 'ml'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port input payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns a classification response."),
                    "error": PortDoc(desc="Returns error.")
                }
            ),
            pro=True
        )
    )
