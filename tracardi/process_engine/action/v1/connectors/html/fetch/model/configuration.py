import json
from json import JSONDecodeError
from typing import Optional, Union
from enum import Enum
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.notation.dot_template import DotTemplate
from pydantic import AnyHttpUrl, BaseModel


class Method(str, Enum):
    post = "post"
    get = "get"
    put = "put"
    delete = 'delete'


class Configuration(BaseModel):
    url: AnyHttpUrl
    timeout: int = 30
    method: Method = Method.get
    headers: Optional[dict] = {}
    cookies: Optional[dict] = {}
    ssl_check: bool = True
    body: str = ""

    def get_params(self, dot: DotAccessor) -> dict:
        dot_template = DotTemplate()
        content = dot_template.render(self.body, dot)
        return {"data": content.encode('utf-8')}
