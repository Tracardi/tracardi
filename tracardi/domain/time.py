from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class Time(BaseModel):
    insert: Optional[datetime]

    def __init__(self, **data: Any):
        data['insert'] = datetime.utcnow()
        super().__init__(**data)

