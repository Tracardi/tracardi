import requests


class ImportDispatcher:

    def __init__(self, credentials, importer, webhook_url: str):
        self.importer = importer
        self.webhook_url = webhook_url
        self.credentials = credentials

    def run(self, tracardi_api_url):
        if tracardi_api_url[-1] == '/':
            tracardi_api_url = tracardi_api_url[:-1]
        for data, progress, batch in self.importer.data(self.credentials):
            url = f"{tracardi_api_url}{self.webhook_url}"
            response = requests.post(url, json=data, verify=False)
            yield progress, batch

