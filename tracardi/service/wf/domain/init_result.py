from pydantic import BaseModel


class InitResult(BaseModel):
    errors: list = []
    objects: list = []
