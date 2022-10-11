import urllib.parse
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.notation.dot_template import DotTemplate
from pydantic import BaseModel
from typing import Optional, Tuple


class ApiCredentials(BaseModel):
    url: str
    proxy: Optional[str] = None
    password: Optional[str] = None
    username: Optional[str] = None

    def _get_url(self) -> Tuple[str, str]:
        url = self.url

        url_chunks = self.url.split("://")

        if len(url_chunks) == 2:
            scheme, url = url_chunks
        elif len(url_chunks) == 1:
            scheme = 'http'
        else:
            raise ValueError("Invalid URL")

        if url[-1] == '/':
            url = url.strip("/")

        return scheme, url

    def get_credentials(self):
        if self.username and self.password:
            return f"{self.username}:{self.password}"
        return None

    def get_url(self, dot: Optional[DotAccessor] = None, endpoint: Optional[str] = None) -> str:

        scheme, url = self._get_url()
        credentials = self.get_credentials()

        if credentials:
            url = f"{scheme}://{credentials}@{url}"
        else:
            url = f"{scheme}://{url}"

        if endpoint:
            if dot is not None:
                template = DotTemplate()
                url += template.render(endpoint, dot)
            else:
                url += endpoint

        return url


class SchemeError(Exception):
    pass


def construct_elastic_url(host: str, scheme: Optional[str] = None, username: Optional[str] = None,
                  password: Optional[str] = None):
    if scheme is None:
        if "://" in host:
            scheme, host = host.split("://")
        else:
            raise SchemeError("No scheme provided for URL.")

    else:
        host = host.split("://")[-1]

    url = scheme + "://"

    if username and password:
        url += f"{username}:{password}@"

    url += host.strip("/")

    if not url.endswith(':9200'):
        url += ':9200'

    return url


def url_query_params_to_dict(url_query_params):
    params = dict(urllib.parse.parse_qs(url_query_params))
    for key, value in params.items():
        if len(value) == 1:
            params[key] = value[0]
    return params
