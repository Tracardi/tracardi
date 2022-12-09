from pydantic import BaseModel, AnyUrl


class DiscordCredentials(BaseModel):
    url: AnyUrl