from typing import List, Optional
from pydantic import field_validator, BaseModel
from tracardi.service.valiadator import validate_email
from datetime import datetime


class UserPayload(BaseModel):
    password: str
    name: str
    email: str
    roles: List[str]
    enabled: bool = False
    expiration_date: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if not validate_email(value):
            raise ValueError("Given e-mail is invalid.")
        return value

    def get_expiration_date(self) -> Optional[int]:
        return None if self.expiration_date is None else \
            int(datetime.strptime(self.expiration_date, "%Y-%m-%d").timestamp())

    def has_admin_role(self):
        return "admin" in self.roles
