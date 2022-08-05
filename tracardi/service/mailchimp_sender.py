import mailchimp_transactional


class MailChimpTransactionalSender:

    def __init__(self, api_key: str):
        self._client = mailchimp_transactional.Client(api_key)
        self._messages = []

    def create_message(self, from_email: str, subject: str, message: str, to_email: str, html_content: bool = False):
        self._messages.append({
            "from_email": from_email,
            "subject": subject,
            "html" if html_content else "text": message,
            "to": [
                {
                    "email": to_email,
                    "type": "to"
                }
            ],
        })

    def send_messages(self):
        results = []
        for message in self._messages:
            try:
                results.append(self._client.messages.send({"message": message}))
            except mailchimp_transactional.api_client.ApiClientError as e:
                raise ValueError(e.text["message"])
        self._messages = []
        return results

    @classmethod
    def validate_api_key(cls, api_key: str):
        if len(api_key) != 22 or not api_key.isalnum():
            raise ValueError("This API key is invalid.")
