import aiohttp
import json


class HubSpotClientException(Exception):
    pass


class HubSpotClientAuthException(Exception):
    pass


class HubSpotClient:

    def __init__(self, refresh_token: str, client_secret: str, client_id: str, token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.token = token

    async def update_token(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url="https://api.hubapi.com/oauth/v1/token",
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
                        "Data": f"grant_type=refresh_token&client_id={self.client_id}&client_secret="
                                f"{self.client_secret}&refresh_token={self.refresh_token}"
                    },
            ) as response:

                if response.status == 401:
                    raise HubSpotClientException("Provided credentials are invalid. Check them in resources.")

                if response.status != 200 or "error" in await response.text() or "errors" in await response.json():
                    raise HubSpotClientException(await response.text())

                self.token = (await response.json())["access_token"]

    async def add_company(self, properties) -> dict:
        data = {"properties": properties}

        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.token}"}) as session:
            async with session.post(
                    url="https://api.hubapi.com/companies/v2/companies",
                    data=data
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def add_contact(self, properties) -> dict:
        data = {"properties": properties}

        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.token}"}) as session:
            async with session.post(
                    url='https://api.hubapi.com/contacts/v1/contact/',
                    data=data
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def add_email(self, properties: list, values: list):

        properties_json = []

        for i in range(0, len(properties)):
            if properties[i] is not None:
                x = {
                    "property": properties[i],
                    "value": values[i]
                }
                properties_json.append(x)

        data = json.dumps({
            "properties": properties_json
            })

        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.token}"}) as session:
            async with session.post(
                    url="https://api.hubapi.com/marketing-emails/v1/emails",
                    data=data
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def get_company(self, company_id: int):
        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.token}"}) as session:
            async with session.get(url=f"https://api.hubapi.com/contacts/v1/contact/vid/{company_id}") as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status != 200 or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def get_contact(self, contact_id: int):
        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.token}"}) as session:
            async with session.get(url=f"https://api.hubapi.com/contacts/v1/contact/vid/{contact_id}") as response:
                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status != 200 or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                contact = list((await response.json())["contacts"].values())[0]
                return {"contact": contact}

    async def update_company(self, company_id, properties) -> dict:
        data = {"properties": properties}

        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.token}"}) as session:
            async with session.post(
                    url=f"https://api.hubapi.com/contacts/v1/contact/vid/{company_id}",
                    data=data
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def update_contact(self, contact_id, properties) -> dict:
        data = {"properties": properties}
        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.token}"}) as session:
            async with session.post(
                    url=f'https://api.hubapi.com/contacts/v1/contact/vid/{contact_id}',
                    data=data
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()


    @property
    def credentials(self):
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "token": self.token
        }
