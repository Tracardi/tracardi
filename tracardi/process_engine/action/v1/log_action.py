from pydantic import BaseModel

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.action_runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Configuration(BaseModel):
    type: str = 'warning'
    message: str


def validate(config: dict):
    return Configuration(**config)


class LogAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
        if self.config.type == 'warning':
            self.console.warning(self.config.message)
        elif self.config.type == 'error':
            self.console.error(self.config.message)
        elif self.config.type == 'info':
            self.console.log(self.config.message)
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='LogAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "type": "warning",
                "message": "<log-message>"
            }
        ),
        metadata=MetaData(
            name='Log message',
            desc='Logs message to flow log.',
            icon='error',
            group=["Error reporting"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port return input payload.")
                }
            )
        )
    )
