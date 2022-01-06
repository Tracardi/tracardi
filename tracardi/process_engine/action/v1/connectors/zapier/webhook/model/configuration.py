from pydantic import AnyHttpUrl, BaseModel


class Configuration(BaseModel):
    url: AnyHttpUrl
    body: str = "{}"
    timeout: int = 10
