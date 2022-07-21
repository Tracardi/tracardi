from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.notation.dot_template import DotTemplate
from pydantic import BaseModel
from typing import Optional


class ApiCredentials(BaseModel):
    url: str
    password: Optional[str] = None
    username: Optional[str] = None


def make_url(credentials: ApiCredentials, dot: Optional[DotAccessor] = None, endpoint: Optional[str] = None) -> str:
    scheme, host = credentials.url.split("://")

    if host[-1] == '/':
        host = host.strip("/")

    url = scheme + "://"
    if credentials.username:
        url += credentials.username
    if credentials.password:
        url += ':' + credentials.password
    if credentials.username or credentials.password:
        url += '@'
    url += host
    if dot is not None and endpoint:
        template = DotTemplate()
        url += template.render(endpoint, dot)
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
    if username:
        url += username
    if password:
        url += ":" + password

    url += host.strip("/")

    if not url.endswith(':9200'):
        url += ':9200'

    return url
