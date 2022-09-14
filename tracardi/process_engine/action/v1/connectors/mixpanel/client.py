import json
from base64 import b64encode
from tracardi.service.tracardi_http_client import HttpClient


class MixPanelAPIClient:

    def __init__(self, server_prefix: str, token: str = None, username: str = None, password: str = None):
        self.server_prefix = "" if server_prefix.lower() == "us" else "-eu"
        self.token = token
        self.username = username
        self.password = password
        self.retries = 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def send(self, event_type: str, profile_id: str, event_id: str, time: int, **kwargs):
        data = {
            "event": event_type,
            "properties": {
                "token": self.token,
                "distinct_id": profile_id,
                "$insert_id": event_id,
                "time": time,
                **kwargs
            }
        }

        async with HttpClient(
            self.retries,
            200,
            headers={
                "Accept": "text/plain",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        ) as client:
            async with client.post(
                    url=f"https://api{self.server_prefix}.mixpanel.com/track?data={json.dumps(data)}&verbose=1",
            ) as response:
                if response.status != 200:
                    raise ConnectionError(response.content)

                return await response.json()

    async def fetch_funnel(self, project_id: int, funnel_id: int, from_date: str, to_date: str, user_id: str):
        params = f"project_id={project_id}&" \
                 f"funnel_id={funnel_id}&" \
                 f"from_date={from_date}&" \
                 f"to_date={to_date}&" \
                 f'where=properties["$distinct_id"]=="{user_id}"'

        async with HttpClient(
            self.retries,
            200,
            headers={
                "Accept": "application/json",
                "Authorization": "Basic " + f"{b64encode(bytes(f'{self.username}:{self.password}', '''utf-8'''))}"[2:-1]
            }
        ) as client:
            async with client.get(
                url=f"https://{self.server_prefix[1:] + '.' if self.server_prefix else ''}mixpanel.com/api/2.0/funnels?"
                    + params
            ) as response:

                if response.status != 200:
                    raise ConnectionError(response.content)

                return await response.json()
