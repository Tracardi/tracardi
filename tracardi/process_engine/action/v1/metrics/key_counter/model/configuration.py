from typing import Union, List
from pydantic import BaseModel


class Configuration(BaseModel):
    key: Union[str, List[str]]
    save_in: str
