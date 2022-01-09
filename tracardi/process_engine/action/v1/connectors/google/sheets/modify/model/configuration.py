from pydantic import BaseModel
from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    source: NamedEntity
    spreadsheet_id: str
    sheet_name: str
    range: str
    read: bool
    write: bool
    values: str
