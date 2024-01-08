import json
from json import JSONDecodeError
from typing import Optional
from enum import Enum

from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.notation.dot_template import DotTemplate

from tracardi.process_engine.tql.utils.dictonary import flatten
from tracardi.domain.named_entity import NamedEntity
from pydantic import BaseModel, validator
from tracardi.service.plugin.domain.config import PluginConfig


class Method(str, Enum):
    post = "post"
    get = "get"
    put = "put"
    delete = 'delete'


class Content(BaseModel):
    type: str
    content: Optional[str] = None

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("content")
    def validate_content(cls, value, values):
        if 'type' in values and values['type'] == 'application/json':
            try:
                # Try parsing JSON
                json.loads(value)
            except JSONDecodeError as e:
                raise ValueError(str(e))
        return value

    def load_body_as_dict(self):
        return json.loads(self.content)


class RemoteCallConfiguration(PluginConfig):
    source: NamedEntity
    endpoint: str
    timeout: int = 30
    method: Method = Method.get
    headers: Optional[dict] = {}
    cookies: Optional[dict] = {}
    ssl_check: Optional[bool] = True
    set_default_null: Optional[bool] = True
    body: Content
    log: Optional[bool] = False

    def get_params(self, dot: DotAccessor, **kwargs) -> dict:
        if self.body.type == 'application/json':
            body = self.body.load_body_as_dict()

            # Use template
            template = DictTraverser(dot, **kwargs)
            body = template.reshape(reshape_template=body)  # type: dict

            if self.method.lower() == 'get':
                params = flatten(body)
                return {
                    "params": params
                }

            return {
                "json": body
            }
        else:
            dot_template = DotTemplate()
            content = dot_template.render(self.body.content, dot)
            return {"data": content.encode('utf-8')}
