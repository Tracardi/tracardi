from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .credentials import TrelloCredentials
from .trello_client import TrelloClient


class TrelloPlugin(ActionRunner):
    _client: TrelloClient

    async def set_up_trello(self, config):
        resource = await storage.driver.resource.load(config.source.id)
        credentials = resource.credentials.get_credentials(self, output=TrelloCredentials)
        client = TrelloClient(credentials.api_key, credentials.token)

        self._client = client
        self._client.set_retries(self.node.on_connection_error_repeat)
