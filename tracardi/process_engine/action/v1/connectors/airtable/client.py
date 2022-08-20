from tracardi.service.tracardi_http_client import HttpClient
from typing import Optional
import json


class AirtableClientException(Exception):
    pass


class AirtableClient:

    def __init__(self, token: str):
        self._token = token
        self.retries = 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def add_record(self, base_id: str, table_name: str, record: dict) -> dict:
        async with HttpClient(
            self.retries,
            200,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json"
            }
        ) as client:
            async with client.post(
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
        async with HttpClient(
                self.retries,
                200,
                headers={
                    "Authorization": f"Bearer {self._token}"
                }
        ) as client:
            async with client.get(
                url=f"https://api.airtable.com/v0/{base_id}/{table_name}?maxRecords=30"
                    f"{'&filterByFormula=' + query if query else ''}"
            ) as response:
                if response.status != 200:
                    raise AirtableClientException(await response.text())

                return await response.json()
