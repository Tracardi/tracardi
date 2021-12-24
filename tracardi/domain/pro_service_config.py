from pydantic import BaseModel, AnyHttpUrl


class TracardiProServiceEndpoint(BaseModel):
    url: AnyHttpUrl
    token: str
    username: str
    password: str


class TracardiProServiceConfig(BaseModel):
    auth: TracardiProServiceEndpoint
    services: str
