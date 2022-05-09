import json
import ssl
import aiohttp
import certifi


class CiviCRMClientException(Exception):
    pass


class CiviCRMClient:

    def __init__(self, api_url: str, api_key: str, site_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.site_key = site_key

    async def add_contact(self, data):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.post(
                url=self.api_url,
                params={
                    "api_key": self.api_key,
                    "key": self.site_key,
                    "json": json.dumps(data),
                    "entity": "Contact",
                    "action": "create"
                }
            ) as response:

                if response.status != 200 or (await response.json())["is_error"] == 1:
                    raise CiviCRMClientException(await response.text())

                return await response.json()

    async def get_custom_fields(self):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            async with session.get(
                url=self.api_url,
                params={
                    "api_key": self.api_key,
                    "key": self.site_key,
                    "entity": "CustomField",
                    "json": json.dumps({"sequential": 1, "return": "id,label,column_name"}),
                    "action": "get"
                }
            ) as response:

                if response.status != 200 or (await response.json())["is_error"] == 1:
                    raise CiviCRMClientException(await response.text())

                result = [{"name": field["label"], "id": f"custom_{field['id']}"} for field in (await response.json())["values"]]

                return {
                    "result": result,
                    "total": len(result)
                }

