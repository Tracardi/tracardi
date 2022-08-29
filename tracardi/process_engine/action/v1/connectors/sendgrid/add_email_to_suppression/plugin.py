from tracardi.domain.resource import Resource
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .model.config import Config, Connection
from ..client import SendgridClient


def validate(config: dict) -> Config:
    return Config(**config)


class SendgridContactAdder(ActionRunner):
    client: SendgridClient
    resource: Resource
    config: Config
    connection: Connection

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.resource = resource
        self.client = SendgridClient(**self.resource.credentials.get_credentials(self, output=Connection))
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        email = dot[self.config.email]

        try:
            result = await self.client.add_email_to_suppression(
                email=email,
            )
            return Result(port="response", value=result)

        except Exception as e:
            return Result(port="error", value={"message": str(e)})
