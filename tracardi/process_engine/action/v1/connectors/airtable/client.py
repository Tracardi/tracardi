import aiohttp
from typing import Optional
import json


class AirtableClientException(Exception):
    pass


class AirtableClient:

    def __init__(self, token: str):
        self._token = token

    async def add_record(self, base_id: str, table_name: str, record: dict) -> dict:
        async with aiohttp.ClientSession(headers={
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }) as session:
            async with session.post(
                url=f"https://api.airtable.com/v0/{base_id}/{table_name}",
                data=json.dumps({
                    "fields": record,
                    "typecast": True
                })
            ) as response:

                if response.status != 200:
                    raise AirtableClientException(await response.text())

                return await response.json()

    async def get_records(self, base_id: str, table_name: str, query: Optional[str]) -> dict:
        async with aiohttp.ClientSession(headers={"Authorization": f"Bearer {self._token}"}) as session:
            async with session.get(
                url=f"https://api.airtable.com/v0/{base_id}/{table_name}?maxRecords=30"
                    f"{'&filterByFormula=' + query if query else ''}"
            ) as response:
                if response.status != 200:
                    raise AirtableClientException(await response.text())

                return await response.json()
