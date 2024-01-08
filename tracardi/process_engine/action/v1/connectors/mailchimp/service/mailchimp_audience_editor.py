import hashlib

import aiohttp
import json
from typing import Dict, Any, List
from tracardi.service.tracardi_http_client import HttpClient


def generate_subscriber_hash(email):
    return hashlib.md5(email.lower().encode('utf-8')).hexdigest()

class MailChimpAudienceEditor:

    def __init__(self, api_key: str, retries: int = 1):
        try:
            self._key, self._server = api_key.split("-")
        except ValueError:
            raise ValueError(f"Incorrect Mailchimp token.")
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

    async def get_contact_fields(self, list_id) -> List[Dict]:
        async with HttpClient(self._retries, [200, 201, 401], headers={"Content-Type": "application/json"}) as client:
            async with client.get(
                    url=f"https://{self._server}.api.mailchimp.com/3.0/lists/{list_id}/merge-fields",
                    auth=aiohttp.BasicAuth("user", self._key)
            ) as response:
                result = await response.json()
                lists = result.get('merge_fields', [])
                return [{"name": l['name'], "id": l['tag']} for l in lists]

    async def get_all_audience_ids(self) -> List[Dict]:
        async with HttpClient(self._retries, [200, 201, 401], headers={"Content-Type": "application/json"}) as client:
            async with client.get(
                    url=f"https://{self._server}.api.mailchimp.com/3.0/lists",
                    auth=aiohttp.BasicAuth("user", self._key)
            ) as response:
                result = await response.json()
                lists = result.get('lists', [])
                return [{"name": l['name'], "id": l['id']} for l in lists]

    async def tag_contact(self, list_id: str, email_address: str, tag_names: List[str]):
        async with HttpClient(self._retries, [200, 201, 401], headers={"Content-Type": "application/json"}) as client:
            subscriber_hash = generate_subscriber_hash(email_address)
            async with client.post(
                    url=f"https://{self._server}.api.mailchimp.com/3.0/lists/{list_id}/members/{subscriber_hash}/tags",
                    data=json.dumps({
                        "tags": [
                            {"name": tag_name, "status": "active"} for tag_name in tag_names
                        ]
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
