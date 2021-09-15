from typing import Optional

from pydantic import BaseModel

from tracardi.domain.consent import Consent


class Consents(BaseModel):
    required: Optional[bool] = True
    list: Optional[Consent] = None
    data_controller_contact: Optional[str] = "Contact site owner"
