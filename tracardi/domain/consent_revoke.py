from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ConsentRevoke(BaseModel):
    revoke: Optional[datetime] = None
