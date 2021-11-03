from typing import Optional, Any
from pydantic import BaseModel


class PII(BaseModel):

    """
    Personally identifiable information, or PII, is any data that could
    potentially be used to identify a particular person. Examples include a full name,
    Social Security number, driver's license number, bank account number,
    passport number, and email address.
    """

    name: Optional[Any] = None
    surname: Optional[Any] = None
    birthDate: Optional[Any] = None
    email: Optional[Any] = None
    telephone: Optional[Any] = None
    twitter: Optional[Any] = None
    facebook: Optional[Any] = None
    whatsapp: Optional[Any] = None
    other: Optional[dict] = {}

