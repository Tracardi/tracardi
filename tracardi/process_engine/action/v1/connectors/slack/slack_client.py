from tracardi.service.tracardi_http_client import HttpClient
import json


class SlackClient:

    def __init__(self, token: str):
        self._token = token
        self.retries = 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def send_to_channel_as_bot(self, channel: str, message: str):
        async with HttpClient(
            self.retries,
            200,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-type": "application/json; charset=utf-8"
            }
        ) as client:
            async with client.post(
                url="https://slack.com/api/chat.postMessage",
                data=json.dumps({
                    "channel": channel,
                    "text": message
                })
            ) as response:

                if response.status != 200:
                    raise ConnectionError("Expected response status 200 got {}".format(response.status))

                result = await response.json()

                if not result["ok"]:
                    raise ConnectionError("Expected OK response {}".format(result))

                return await response.json()

