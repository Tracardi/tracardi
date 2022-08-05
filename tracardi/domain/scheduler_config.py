from pydantic import BaseModel


class SchedulerConfig(BaseModel):
    callback_host: str
