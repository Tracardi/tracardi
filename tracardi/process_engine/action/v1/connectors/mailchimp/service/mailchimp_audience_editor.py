import aiohttp
import json
from typing import Dict, Any
from tracardi.service.tracardi_http_client import HttpClient


class MailChimpAudienceEditor:

    def __init__(self, api_key: str, retries: int = 1):
        self._key, self._server = api_key.split("-")
        self._retries = retries

    async def add_contact(self, list_id: str, email_address: str, subscribed: bool, merge_fields: Dict[str, Any]):
        async with HttpClient(self._retries, [200, 201, 401], headers={"Content-Type": "application/json"}) as client:
            async with client.post(
                    url=f"https://{self._server}.api.mailchimp.com/3.0/lists/{list_id}/members",
                    data=json.dumps({
                        "email_address": email_address,
                        "status": "subscribed" if subscribed else "pending",
                        "merge_fields": merge_fields
                    }),
                    auth=aiohttp.BasicAuth("user", self._key)
            ) as response:
                return await response.json()

    async def update_contact(self, list_id: str, email_address: str, subscribed: bool, merge_fields: Dict[str, Any]):
        async with HttpClient(self._retries, [200, 201, 401], headers={"Content-Type": "application/json"}) as client:
            async with client.put(
                    url=f"https://{self._server}.api.mailchimp.com/3.0/lists/{list_id}/members/{email_address}",
                    data=json.dumps({
                        "email_address": email_address,
                        "status": "subscribed" if subscribed else "pending",
                        "merge_fields": merge_fields
                    }),
                    auth=aiohttp.BasicAuth("user", self._key)
            ) as response:
                return await response.json()

    async def archive_contact(self, list_id: str, email_address: str):
        async with HttpClient(self._retries, [200, 201, 401], headers={"Content-Type": "application/json"}) as client:
            async with client.delete(
                    url=f"https://{self._server}.api.mailchimp.com/3.0/lists/{list_id}/members/{email_address}",
                    auth=aiohttp.BasicAuth("user", self._key)
            ) as response:
                return await response.json()

    async def delete_contact(self, list_id: str, email_address: str):
        async with HttpClient(self._retries, [200, 201, 401], headers={"Content-Type": "application/json"}) as client:
            async with client.post(
                    url=f"https://{self._server}.api.mailchimp.com/3.0/lists/{list_id}/members/{email_address}/"
                        f"actions/delete-permanent",
                    auth=aiohttp.BasicAuth("user", self._key)
            ) as response:
                return await response.json()
