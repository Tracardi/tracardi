from tracardi.service.tracardi_http_client import HttpClient


class SendgridClientException(Exception):
    pass


class SendgridClientAuthException(Exception):
    pass


class SendgridClient:

    def __init__(self, api_key: str):
        self.api_url = 'https://api.sendgrid.com'
        self.api_key = api_key
        self.retries = 1

    def set_retries(self, retries: int) -> None:
        self.retries = retries

    async def add_email_to_suppression(self, email: str, **kwargs) -> dict:
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
                    data=data
            ) as response:

                if response.status == 401:
                    raise SendgridClientAuthException()

                if response.status not in (200, 201) or "error" in await response.text() or "errors" in \
                        await response.json():
                    raise SendgridClientException(await response.text())

                return await response.json()
