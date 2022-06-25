from typing import Optional
from enum import Enum
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.notation.dot_template import DotTemplate
from pydantic import AnyHttpUrl, BaseModel
from tracardi.service.plugin.domain.config import PluginConfig


class Method(str, Enum):
    post = "post"
    get = "get"
    put = "put"
    delete = 'delete'


class Configuration(PluginConfig):
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
