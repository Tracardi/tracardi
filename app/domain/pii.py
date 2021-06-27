from typing import Optional

from pydantic import BaseModel


class PII(BaseModel):
    """
    Personally identifiable information, or PII, is any data that could
    potentially be used to identify a particular person. Examples include a full name,
    Social Security number, driver's license number, bank account number,
    passport number, and email address.
    """
    name: Optional[str] = ''
    surname: Optional[str] = ''
    birthDate: Optional[int] = None
    email: Optional[str] = ''
    telephone: Optional[str] = ''
    other: Optional[dict] = {}
