from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.notation.dot_template import DotTemplate
from pydantic import BaseModel
from typing import Optional


class ApiCredentials(BaseModel):
    url: str
    password: Optional[str] = None
    username: Optional[str] = None


def make_url(credentials: ApiCredentials, dot: DotAccessor, endpoint: str) -> str:
    scheme, host = credentials.url.split("://")

    if host[-1] == '/':
        host = host[:-1]

    url = scheme + "://"
    if credentials.username:
        url += credentials.username
    if credentials.password:
        url += ':' + credentials.password
    if credentials.username or credentials.password:
        url += '@'
    url += host
    template = DotTemplate()
    url += template.render(endpoint, dot)
    return url
