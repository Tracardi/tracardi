import json
from json import JSONDecodeError
from typing import Optional, Union
from enum import Enum

from tracardi_dot_notation.dict_traverser import DictTraverser
from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi_dot_notation.dot_template import DotTemplate

from tracardi.process_engine.tql.utils.dictonary import flatten
from pydantic import AnyHttpUrl, BaseModel, validator


class Method(str, Enum):
    post = "post"
    get = "get"
    put = "put"
    delete = 'delete'


class Content(BaseModel):
    type: str
    content: Optional[str]

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


class RemoteCallConfiguration(BaseModel):
    url: AnyHttpUrl
    timeout: int = 30
    method: Method = Method.get
    headers: Optional[dict] = {}
    cookies: Optional[dict] = {}
    ssl_check: bool = True
    body: Content

    def get_params(self, dot: DotAccessor) -> dict:
        if self.body.type == 'application/json':
            body = self.body.load_body_as_dict()

            # Use template
            template = DictTraverser(dot)
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
