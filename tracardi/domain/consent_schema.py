from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ConsentSchema(BaseModel):
    type_id: UUID
    revoke: datetime = datetime.utcnow()
