from pydantic import BaseModel

from tracardi.service.valiadator import validate_email


class Credentials(BaseModel):
    username: str
    password: str

    def not_empty(self) -> bool:
        return self.password != "" and self.username != ""

    def username_as_email(self) -> bool:
        return validate_email(self.username)
