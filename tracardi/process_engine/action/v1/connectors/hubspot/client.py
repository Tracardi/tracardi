import aiohttp
import json


class HubSpotClientException(Exception):
    pass


class HubSpotClientAuthException(Exception):
    pass


class HubSpotClient:

    def __init__(self, client_secret: str, client_id: str, access_token: str, refresh_token: str, redirect_url: str,
                 code: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.redirect_url = redirect_url
        self.code = code

    def change_properties_form(self, properties, key):
        prop_keys = list(properties.keys())
        properties_array = []

        for i in range(len(prop_keys)):
            subdict = {
                key: f"{prop_keys[i]}",
                "value": f"{properties[prop_keys[i]]}"
               }
            properties_array.append(subdict)

        return properties_array

    async def get_token(self) -> None:
        async with aiohttp.ClientSession() as session:

            async with session.post(
                    url="https://api.hubapi.com/oauth/v1/token",
                    data={
                        'grant_type': 'authorization_code',
                        'client_id': f'{self.client_id}',
                        'client_secret': f'{self.client_secret}',
                        'redirect_uri': f'{self.redirect_url}',
                        'code': f'{self.code}'
                    }
            ) as response:

                if response.status == 401:
                    raise HubSpotClientException("Provided credentials are invalid. Check them in resources.")

                if response.status != 200 or "error" in await response.text() or "errors" in await response.json():
                    raise HubSpotClientException(await response.text())

                self.access_token = (await response.json())["access_token"]
                self.refresh_token = (await response.json())["refresh_token"]

                return self.refresh_token, self.access_token

    async def update_token(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url="https://api.hubapi.com/oauth/v1/token",
                    data={
                        'grant_type': 'refresh_token',
                        'client_id': f'{self.client_id}',
                        'client_secret': f'{self.client_secret}',
                        'refresh_token': f'{self.refresh_token}',
                    }
            ) as response:

                if response.status == 401:
                    raise HubSpotClientException("Provided credentials are invalid. Check them in resources.")

                if response.status != 200 or "error" in await response.text() or "errors" in await response.json():
                    raise HubSpotClientException(await response.text())

                self.access_token = (await response.json())["access_token"]
                self.refresh_token = (await response.json())["refresh_token"]

                return self.refresh_token, self.access_token

    async def add_company(self, properties) -> dict:
        properties_array = self.change_properties_form(properties, "name")
        data = {"properties": properties_array}

        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.access_token}"}) as session:
            async with session.post(
                    url="https://api.hubapi.com/companies/v2/companies",
                    data=json.dumps(data)
            ) as response:

                print(json.dumps(data))

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def add_contact(self, properties) -> dict:
        properties_array = self.change_properties_form(properties, "property")
        data = {"properties": properties_array}

        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.access_token}"}) as session:
            async with session.post(
                    url='https://api.hubapi.com/contacts/v1/contact/',
                    data=json.dumps(data)
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def add_email(self, properties) -> dict:

        data = json.dumps(properties)
        print(data)

        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.access_token}"}) as session:
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

    async def get_company(self, company_id: int) -> dict:
        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.access_token}"}) as session:
            async with session.get(url=f"https://api.hubapi.com/companies/v2/companies/{company_id}") as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status != 200 or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def get_contact(self, contact_id: int) -> dict:
        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.access_token}"}) as session:
            async with session.get(url=f"https://api.hubapi.com/contacts/v1/contact/vid/{contact_id}/profile") as \
                    response:
                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status != 200 or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def update_company(self, company_id, properties) -> dict:
        properties_array = self.change_properties_form(properties, "name")
        data = {"properties": properties_array}

        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.access_token}"}) as session:
            async with session.put(
                    url=f"https://api.hubapi.com/companies/v2/companies/{company_id}",
                    data=json.dumps(data)
            ) as response:

                if response.status == 401:
                    raise HubSpotClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise HubSpotClientException(await response.text())

                return await response.json()

    async def update_contact(self, contact_id, properties) -> dict:
        properties_array = self.change_properties_form(properties, "property")
        data = {"properties": properties_array}

        async with aiohttp.ClientSession(headers={'Content-Type': "application/json",
                                                  "Authorization": f"Bearer {self.access_token}"}) as session:
            async with session.post(
                    url=f"https://api.hubapi.com/contacts/v1/contact/vid/{contact_id}/profile",
                    data=json.dumps(data)
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
            "access_token": self.access_token,
            "redirect_url": self.redirect_url,
            "code": self.code,
        }
