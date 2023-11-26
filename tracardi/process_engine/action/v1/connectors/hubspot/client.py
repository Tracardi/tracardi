from tracardi.service.tracardi_http_client import HttpClient


class HubSpotClientException(Exception):
    pass


class HubSpotClientAuthException(Exception):
    pass


class HubSpotClient:

    def __init__(self, token: str):
        self.access_token = token
        self.retries = 1
        self.api_url = 'https://api.hubapi.com'
        self.auth_headers = {'Content-Type': "application/json", "Authorization": f"Bearer {self.access_token}"}

    def set_retries(self, retries: int):
        self.retries = retries


    async def create_list(self, list_name: str):
        data = {
            "objectTypeId": "0-1",
            "name": list_name,
            "processingType": "MANUAL"
        }

        async with HttpClient(self.retries, [200, 401], headers=self.auth_headers) as session:
            async with session.post(
                    url=f"{self.api_url}/crm/v3/lists",
                    json=data
            ) as response:

                print(response)

                return await response.json()

    async def add_contact_to_list(self, list_id, contact_ids):

        data = {
            "inputs": [{"id": contact_id} for contact_id in contact_ids]
        }

        async with HttpClient(self.retries, [200, 401], headers=self.auth_headers) as session:
            async with session.post(
                    url=f"{self.api_url}/crm/v3/objects/contact_lists/{list_id}/contacts",
                    json=data
            ) as response:

                print(response)

                return await response.json()

    async def add_company(self, properties) -> dict:
        data = {"properties": properties}
        async with HttpClient(self.retries, [200, 401], headers=self.auth_headers) as session:
            async with session.post(
                    url=f"{self.api_url}/crm/v3/objects/companies",
                    json=data
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def add_contact(self, properties) -> dict:
        data = {"properties": properties}
        async with HttpClient(self.retries, [200, 401], headers=self.auth_headers) as session:
            async with session.post(
                    url=f"{self.api_url}/crm/v3/objects/contacts",
                    json=data
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def get_company(self, company_id: str) -> dict:
        async with HttpClient(self.retries, [200, 401], headers=self.auth_headers) as session:
            async with session.get(
                    url=f"{self.api_url}/crm/v3/objects/companies/{company_id}",
            ) as response:
                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status != 200 or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def get_contact(self, contact_id: int) -> dict:
        async with HttpClient(self.retries, [200, 401], headers=self.auth_headers) as session:
            async with session.get(
                    url=f"{self.api_url}/crm/v3/objects/contacts/{contact_id}",
            ) as response:
                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status != 200 or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def update_company(self, company_id, properties) -> dict:
        data = {"properties": properties}
        async with HttpClient(self.retries, [200, 401], headers=self.auth_headers) as session:
            async with session.patch(
                    url=f"{self.api_url}/crm/v3/objects/companies/{company_id}",
                    json=data
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def update_contact(self, contact_id, properties) -> dict:
        data = {"properties": properties}
        async with HttpClient(self.retries, [200, 401], headers=self.auth_headers) as session:
            async with session.patch(
                    url=f"{self.api_url}/crm/v3/objects/contacts/{contact_id}",
                    json=data
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return response.json()

    @property
    def credentials(self):
        return {
            "access_token": self.access_token,
        }
