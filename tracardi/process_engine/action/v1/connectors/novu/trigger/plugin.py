import json
from hashlib import sha1
from json import JSONDecodeError
from typing import Optional

import aiohttp

from tracardi.domain.resources.api_url_with_token import ApiUrlToken
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from tracardi.service.tracardi_http_client import HttpClient
from tracardi.service.domain import resource as resource_db
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class Config(PluginConfig):
    source: NamedEntity
    template: NamedEntity
    subscriber_id: str
    recipient_email: Optional[str] = ""
    payload: Optional[str] = "{}"
    hash: bool = False
    upsert_subscriber: bool = True
    tenant: Optional[NamedEntity] = None


def validate(config: dict) -> Config:
    return Config(**config)


class Endpoint(PluginEndpoint):

    @staticmethod
    async def get_templates(config: dict):
        config = Config(**config)
        if config.source.is_empty():
            raise ValueError("Resource not set.")

        resource = await resource_db.load(config.source.id)
        creds = ApiUrlToken(**resource.credentials.production)
        timeout = aiohttp.ClientTimeout(total=15)
        async with HttpClient(2, [200, 201, 202, 203], timeout=timeout) as client:
            async with client.get(
                    url=f"{creds.host}/v1/workflows",
                    headers={"Authorization": f"ApiKey {creds.token}",
                             "Content Type": "application/json"},
                    ssl=True
            ) as response:
                content = await response.json()

                if 'data' not in content:
                    raise ValueError("Could not retrieve data from remote server.")

                result = [{"id": item['triggers'][0]['identifier'], "name": item['name']} for item in content['data'] if
                          item['active'] is True]
                return {
                    "total": len(result),
                    "result": result
                }


    async def get_tenants(config: dict):

        config = Config(**config)
        if config.source.is_empty():
            raise ValueError("Resource not set.")

        resource = await resource_db.load(config.source.id)
        creds = ApiUrlToken(**resource.credentials.production)
        timeout = aiohttp.ClientTimeout(total=15)
        async with HttpClient(2, [200, 201, 202, 203], timeout=timeout) as client:
            async with client.get(
                    url=f"{creds.host}/v1/tenants?limit=100",
                    headers={"Authorization": f"ApiKey {creds.token}",
                             "Content Type": "application/json"},
                    ssl=True
            ) as response:
                content = await response.json()

                if 'data' not in content:
                    raise ValueError("Could not retrieve data from remote server.")

                result = [{"id": item['_id'], "name": item['name']} for item in content['data']]
                return {
                    "total": len(result),
                    "result": result
                }

class NovuTriggerAction(ActionRunner):
    credentials: ApiUrlToken
    config: Config

    async def _trigger_workflow(self, subscriber_id: str, email: str, payload: dict):

        params = {
            "name": self.config.template.id,
            "to": {
                "subscriberId": subscriber_id,
                "email": email
            },
            "payload": payload
        }

        timeout = aiohttp.ClientTimeout(total=15)
        async with HttpClient(self.node.on_connection_error_repeat,
                              [200, 201, 202, 203],
                              timeout=timeout) as client:
            async with client.post(
                    url=f'{self.credentials.host}/v1/events/trigger',  # https://api.novu.co
                    headers={"Authorization": f"ApiKey {self.credentials.token}",
                             "Content Type": "application/json"},
                    ssl=False,
                    json=params
            ) as response:
                return response

    async def _add_subscriber(self, novu_payload):
        timeout = aiohttp.ClientTimeout(total=15)
        async with HttpClient(self.node.on_connection_error_repeat, [200, 201, 202, 203],
                              timeout=timeout) as client:
            async with client.post(
                    url='https://api.novu.co/v1/subscribers',
                    headers={"Authorization": f"ApiKey {self.credentials.token}",
                             "Content Type": "application/json"},
                    ssl=False,
                    json=novu_payload
            ) as response:
                return response

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=ApiUrlToken)

    async def run(self, payload: dict, in_edge=None) -> Result:

        if not self.profile:
            message = f"Could not run Novu Trigger Workflow when there is no profile."
            return self.get_error_result(message, port="error")

        dot = self._get_dot_accessor(payload)
        subscriber_id = dot[self.config.subscriber_id]

        if subscriber_id is None:
            message = f"Defined subscriber id {self.config.subscriber_id} did not returned any data. "
            return self.get_error_result(message, port="error")

        subscriber_id = sha1(subscriber_id.encode()).hexdigest() if self.config.hash else subscriber_id

        email = dot[self.config.recipient_email]

        if not email:
            message = "Profile has not e-mail so no message can be send via Novu."
            return self.get_error_result(message, port="error")

        if self.config.upsert_subscriber is True:
            novu_namespace = self.profile.aux.get('novu', None)
            if not novu_namespace:
                self.profile.aux['novu'] = {
                    "registered": False
                }
            if self.profile.aux['novu']['registered'] is False:

                self.console.log(f"Registering NOVU subscriber ID {subscriber_id} with email {email}")

                novu_payload = dict(
                    email=email,
                    subscriberId=subscriber_id,
                    firstName=self.profile.data.pii.firstname,
                    lastName=self.profile.data.pii.lastname,
                    phone=self.profile.data.contact.phone.main
                )

                response = await self._add_subscriber(novu_payload)
                try:
                    content = await response.json()
                except JSONDecodeError:
                    content = await response.text()

                if response.status not in [200, 201, 202, 203]:
                    message = f"Could not register subscriber, Detail: {content}."
                    return self.get_error_result(message, port="error")

                self.console.log(f"NOVU subscriber ID {subscriber_id} registered, response: {content}")

                self.profile.aux['novu']['registered'] = True
                self.update_profile()

        novu_payload = json.loads(self.config.payload)
        template = DictTraverser(dot)
        novu_payload = template.reshape(novu_payload)
        response = await self._trigger_workflow(subscriber_id,
                                                email,
                                                novu_payload)

        try:
            content = await response.json()
        except JSONDecodeError:
            content = await response.text()

        result = {
            "status": response.status,
            "content": content
        }

        if response.status in [200, 201, 202, 203]:
            return Result(port="response", value=result)
        else:
            return Result(port="error", value=result)
