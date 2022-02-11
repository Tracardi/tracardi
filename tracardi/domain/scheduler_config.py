from pydantic import BaseModel


class SchedulerConfig(BaseModel):
    token: str
    host: str
    callback_host: str
