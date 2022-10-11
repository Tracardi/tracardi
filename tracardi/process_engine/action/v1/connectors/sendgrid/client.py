from json import JSONDecodeError

from tracardi.service.tracardi_http_client import HttpClient


class SendgridClientException(Exception):
    pass


class SendgridClientAuthException(Exception):
    pass


class SendgridClient:

    def __init__(self, token: str):
        self.api_url = 'https://api.sendgrid.com'
        self.api_key = token
        self.retries = 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def add_contact_to_list(self, email_params: dict, **kwargs) -> dict:
        async with HttpClient(
                self.retries,
                [200, 201, 202, 401],
                headers={"Authorization": f"Bearer {self.api_key}"}
        ) as client:
            async with client.put(
                    url=f"{self.api_url}/v3/marketing/contacts",
                    json=email_params
            ) as response:

                if response.status == 401:
                    raise SendgridClientAuthException()

                if response.status not in (200, 201, 202):
                    raise SendgridClientException(await response.text())
                try:
                    content = await response.json()
                except JSONDecodeError:
                    content = await response.text()
                return content

    async def emails_post(self, email_params: dict, **kwargs) -> dict:
        async with HttpClient(
                self.retries,
                [200, 201, 202, 401],
                headers={"Authorization": f"Bearer {self.api_key}"}
        ) as client:
            async with client.post(
                    url=f"{self.api_url}/v3/mail/send",
                    json=email_params
            ) as response:

                if response.status == 401:
                    raise SendgridClientAuthException()

                if response.status not in (200, 201, 202):
                    raise SendgridClientException(await response.text())
                try:
                    content = await response.json(content_type='text/plain')
                except JSONDecodeError:
                    content = await response.text()
                return content

    async def add_email_to_global_suppression(self, email: str, **kwargs) -> dict:
        data = {
            "recipient_emails": [email, ],
        }

        async with HttpClient(
                self.retries,
                [200, 201, 401],
                headers={"Authorization": f"Bearer {self.api_key}"}
        ) as client:
            async with client.post(
                    url=f"{self.api_url}/v3/asm/suppressions/global",
                    json=data
            ) as response:

                if response.status == 401:
                    raise SendgridClientAuthException()

                if response.status not in (200, 201):
                    raise SendgridClientException(await response.text())
                try:
                    content = await response.json(content_type='text/plain')
                except JSONDecodeError:
                    content = await response.text()
                return content
