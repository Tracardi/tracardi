from tracardi.service.tracardi_http_client import HttpClient


class MauticClientException(Exception):
    pass


class MauticClientAuthException(Exception):
    pass


class MauticClient:

    def __init__(self, api_url: str, public_key: int, private_key: str, token: str = ""):
        self.api_url = api_url
        self.public_key = public_key
        self.private_key = private_key
        self.token = token
        self.retries = 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def update_token(self) -> None:
        async with HttpClient(self.retries, [200, 401]) as client:
            async with client.post(
                    url=f"{self.api_url}/oauth/v2/token",
                    data={
                        "client_id": self.public_key,
                        "client_secret": self.private_key,
                        "grant_type": "client_credentials"
                    }
            ) as response:

                if response.status == 401:
                    raise MauticClientException("Provided credentials are invalid. Check them in resources.")

                if response.status != 200 or "error" in await response.text() or "errors" in await response.json():
                    raise MauticClientException(await response.text())

                self.token = (await response.json())["access_token"]

    async def add_contact(self, email: str, overwrite_with_blank: bool, **kwargs) -> dict:
        data = {
            "email": email,
            **kwargs
        }
        if overwrite_with_blank is True:
            data["overwriteWithBlank"] = True

        async with HttpClient(
            self.retries,
            [200, 201, 401],
            headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.post(
                    url=f"{self.api_url}/api/contacts/new",
                    data=data
            ) as response:

                if response.status == 401:
                    raise MauticClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise MauticClientException(await response.text())

                return await response.json()

    async def fetch_contact_by_id(self, id: str):
        async with HttpClient(
                self.retries,
                [200, 401],
                headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.get(url=f"{self.api_url}/api/contacts/{id}") as response:

                if response.status == 401:
                    raise MauticClientAuthException()

                if response.status != 200 or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise MauticClientException(await response.text())

                return await response.json()

    async def fetch_contact_by_email(self, email: str):
        async with HttpClient(
                self.retries,
                [200, 401],
                headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.get(url=f"{self.api_url}/api/contacts?search=email:{email}") as response:

                if response.status == 401:
                    raise MauticClientAuthException()

                if response.status != 200 or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise MauticClientException(await response.text())

                try:
                    contact = list((await response.json())["contacts"].values())[0]
                    return {"contact": contact}

                except KeyError:
                    raise MauticClientException(f"Unable to find contact with given email address: {email}")

    async def add_points(self, id: int, amount: int):
        async with HttpClient(
                self.retries,
                [200, 401],
                headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.post(url=f"{self.api_url}/api/contacts/{id}/points/plus/{amount}") as response:

                if response.status == 401:
                    raise MauticClientAuthException()

                if response.status != 200:
                    raise MauticClientException(await response.text())

                return await response.json()

    async def subtract_points(self, id: int, amount: int):
        async with HttpClient(
                self.retries,
                [200, 401],
                headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.post(url=f"{self.api_url}/api/contacts/{id}/points/minus/{amount}") as response:

                if response.status == 401:
                    raise MauticClientAuthException()

                if response.status != 200:
                    raise MauticClientException(await response.text())

                return await response.json()

    async def add_to_segment(self, id: int, add_to: int):
        async with HttpClient(
                self.retries,
                [200, 401],
                headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.post(url=f"{self.api_url}/api/segments/{add_to}/contact/{id}/add") \
                    as response:

                if response.status == 401:
                    raise MauticClientAuthException()

                if response.status != 200:
                    raise MauticClientException(await response.text())

    async def remove_from_segment(self, id: int, remove_from: int):
        async with HttpClient(
                self.retries,
                [200, 401],
                headers={"Authorization": f"Bearer {self.token}"}
        ) as client:
            async with client.post(url=f"{self.api_url}/api/segments/{remove_from}/contact/{id}/remove") \
                    as response:

                if response.status == 401:
                    raise MauticClientAuthException()

                if response.status != 200:
                    raise MauticClientException(await response.text())

                return await response.json()

    @property
    def credentials(self):
        return {
            "public_key": self.public_key,
            "private_key": self.private_key,
            "api_url": self.api_url,
            "token": self.token
        }
