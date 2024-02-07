import urllib.parse
from tracardi.service.domain import resource as resource_db

from tracardi.exceptions.log_handler import get_logger
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.notation.dot_template import DotTemplate
from .model.pushover_config import PushOverConfiguration, PushOverAuth
from tracardi.service.tracardi_http_client import HttpClient

logger = get_logger(__name__)

def validate(config: dict) -> PushOverConfiguration:
    return PushOverConfiguration(**config)


class PushoverAction(ActionRunner):

    credentials: PushOverAuth
    pushover_config: PushOverConfiguration

    async def set_up(self, init):
        config = validate(init)
        source = await resource_db.load(config.source.id)

        self.pushover_config = config
        self.credentials = source.credentials.get_credentials(self, output=PushOverAuth)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            async with HttpClient(self.node.on_connection_error_repeat) as client:

                dot = self._get_dot_accessor(payload)
                template = DotTemplate()

                data = {
                    "token": self.credentials.token,
                    "user": self.credentials.user,
                    "message": template.render(self.pushover_config.message, dot)
                }

                async with client.post(
                    url='https://api.pushover.net/1/messages.json',
                    data=urllib.parse.urlencode(data),
                    headers={"Content-type": "application/x-www-form-urlencoded"}
                ) as response:

                    if response.status != 200:
                        result = await response.json()
                        message = f"Could not connect to Pushover API. Error port triggered with the response {result}"
                        logger.error(message)
                        self.console.error(message)
                        return Result(port="error", value={
                            "message": "Could not connect to Pushover API.",
                            "status": response.status,
                            "response": result
                        })

                    return Result(port="payload", value={
                        "status": response.status,
                        "response": await response.json()
                    })

        except Exception as e:
            return Result(port="error", value={
                "message": repr(e),
                "status": None,
                "response": None
            })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='PushoverAction',
            inputs=["payload"],
            outputs=['payload', 'error'],
            version='0.7.1',
            license="MIT + CC",
            author="Bartosz Dobrosielski, Risto Kowaczewski",
            manual="send_pushover_msg_action"
        ),
        metadata=MetaData(
            name='Pushover push',
            desc='Connects to Pushover app and pushes message.',
            icon='pushover',
            group=["Messaging"],
            tags=['messaging'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns a response from Pushover API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            ),
            pro=True
        )
    )
