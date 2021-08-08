from typing import Optional

from pydantic import BaseModel


class SqlQuery(BaseModel):
    where: Optional[str] = None
    limit: Optional[int] = 20

