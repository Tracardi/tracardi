import aiohttp
import json


class SlackClient:

    def __init__(self, token: str):
        self._token = token

    async def send_to_channel_as_bot(self, channel: str, message: str):
        async with aiohttp.ClientSession(headers={
            "Authorization": f"Bearer {self._token}",
            "Content-type": "application/json; charset=utf-8"
        }) as session:
            async with session.post(
                url="https://slack.com/api/chat.postMessage",
                data=json.dumps({
                    "channel": channel,
                    "text": message
                })
            ) as response:

                if response.status != 200 or not (await response.json())["ok"]:
                    raise ConnectionError("Expected response status 200 got {}".format(response.status))

                return await response.json()

